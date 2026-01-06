from typing import List, Optional
import os
import re
from spss_engine.lexer import SpssLexer
from spss_engine.parser import SpssParser, TokenType
from spss_engine.extractor import AssignmentExtractor
from spss_engine.state import StateMachine, VariableVersion

class CompilerPipeline:
    def __init__(self):
        self.parser = SpssParser()
        self.extractor = AssignmentExtractor()
        self.state_machine = StateMachine()

    def process(self, raw_code: str):
        lexer = SpssLexer(raw_code)
        commands = lexer.get_commands()

        for command in commands:
            parsed = self.parser.parse_command(command)
            cmd_type = parsed.type

            # --- 1. Assignments ---
            if cmd_type == TokenType.ASSIGNMENT:
                self._handle_assignment(command)

            # --- 2. Conditional (Implicit Assignment check) ---
            elif cmd_type == TokenType.CONDITIONAL:
                # Register the branching event
                self.state_machine.register_conditional(command)
                
                # CRITICAL FIX: Check if this IF statement contains an assignment!
                # Logic: If extract_target finds a variable, treat it as an assignment too.
                # Example: "IF (x) COMPUTE y = 1" -> target is "y"
                target = self.extractor.extract_target(command)
                if target:
                     self._handle_assignment(command)

            # --- 3. File I/O ---
            elif cmd_type == TokenType.FILE_SAVE:
                filename = self.extractor.extract_file_target(command)
                if filename:
                    self.state_machine.register_file_save(filename, command)

            elif cmd_type == TokenType.FILE_MATCH:
                filename = self.extractor.extract_file_target(command)
                if filename:
                    self.state_machine.register_file_match(filename, command)

            # --- 4. Control Flow ---
            elif cmd_type == TokenType.CONTROL_FLOW:
                self.state_machine.register_control_flow(command)

    def _handle_assignment(self, command: str):
        """Helper to process assignment logic, shared by ASSIGNMENT and CONDITIONAL types."""
        target_var = self.extractor.extract_target(command)
        
        if target_var:
            raw_deps = self.extractor.extract_dependencies(command)
            resolved_deps = []
            
            for dep_name in raw_deps:
                # Filter Self-Reference (Left-Hand Side)
                if dep_name.upper() == target_var.upper():
                    continue 

                try:
                    current_ver = self.state_machine.get_current_version(dep_name)
                    resolved_deps.append(current_ver)
                except ValueError:
                    pass

            self.state_machine.register_assignment(
                target_var, 
                source_code=command, 
                dependencies=resolved_deps
            )

    def analyze_dead_code(self) -> List[str]:
        return self.state_machine.find_dead_versions()

    def process_file(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            self.process(f.read())

    def get_variable_version(self, var_name: str) -> Optional[VariableVersion]:
        """
        FIX: Returns the actual VariableVersion object (last known state), 
        not just the ID string. This fixes the attribute errors in tests.
        """
        history = self.state_machine.get_history(var_name)
        if history:
            return history[-1]
        return None

    def get_variable_history(self, var_name: str):
        return self.state_machine.get_history(var_name)