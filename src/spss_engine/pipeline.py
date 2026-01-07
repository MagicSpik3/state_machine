from typing import List, Optional
import os
from spss_engine.lexer import SpssLexer
from spss_engine.parser import SpssParser, TokenType
from spss_engine.extractor import AssignmentExtractor
from spss_engine.state import StateMachine, VariableVersion

class CompilerPipeline:
    def __init__(self):
        self.parser = SpssParser()
        self.extractor = AssignmentExtractor()
        self.state_machine = StateMachine()
        self.join_counter = 0  # Counter for generating unique System IDs

    def process(self, raw_code: str):
        lexer = SpssLexer(raw_code)
        commands = lexer.get_commands()

        for command in commands:
            parsed = self.parser.parse_command(command)
            cmd_type = parsed.type

            # --- 1. Assignments ---
            if cmd_type == TokenType.ASSIGNMENT:
                self._handle_assignment(command)

            # --- 2. Conditional ---
            elif cmd_type == TokenType.CONDITIONAL:
                self.state_machine.register_conditional(command)
                target = self.extractor.extract_target(command)
                if target:
                     self._handle_assignment(command)

            # --- 3. File I/O (MATCH FILES) ---
            elif cmd_type == TokenType.FILE_MATCH:
                # FIX: We treat Match Files as a "System Assignment" so it appears in the graph
                # and isn't prone to "Unknown Method" errors on the state machine.
                self.join_counter += 1
                sys_id = f"###SYS_JOIN_{self.join_counter}###"
                self.state_machine.register_assignment(sys_id, command, dependencies=[])

            # --- 4. Control Flow ---
            elif cmd_type == TokenType.CONTROL_FLOW:
                self.state_machine.register_control_flow(command)

    def _handle_assignment(self, command: str):
        target_var = self.extractor.extract_target(command)
        if target_var:
            raw_deps = self.extractor.extract_dependencies(command)
            resolved_deps = []
            for dep_name in raw_deps:
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
        """
        Identifies variables that are calculated but never used.
        FIX: Whitelists ###SYS_ nodes so Joins aren't deleted.
        """
        raw_dead_ids = self.state_machine.find_dead_versions()
        
        # Filter out System Nodes (The Fix)
        filtered_ids = [vid for vid in raw_dead_ids if "###SYS_" not in vid]
        
        return filtered_ids

    def process_file(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            self.process(f.read())

    def get_variable_version(self, var_name: str) -> Optional[VariableVersion]:
        history = self.state_machine.get_history(var_name)
        if history:
            return history[-1]
        return None

    def get_variable_history(self, var_name: str):
        return self.state_machine.get_history(var_name)