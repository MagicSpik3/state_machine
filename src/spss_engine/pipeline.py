from typing import List, Optional, Callable, Dict
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
        self.join_counter = 0

        # --- Refactor: Dispatch Table ---
        # Maps TokenType to specific handler methods.
        self.dispatch_table: Dict[TokenType, Callable[[str], None]] = {
            TokenType.ASSIGNMENT: self._handle_assignment,
            TokenType.CONDITIONAL: self._handle_conditional,
            TokenType.FILE_MATCH: self._handle_file_match,
            TokenType.CONTROL_FLOW: self._handle_control_flow,
            TokenType.AGGREGATE: self._handle_aggregate,  # New Feature
            # TokenType.FILE_SAVE is often handled implicitly or ignored in logic graphs, 
            # but can be added here if needed.
        }

    def process(self, raw_code: str):
        lexer = SpssLexer(raw_code)
        commands = lexer.get_commands()

        for command in commands:
            parsed = self.parser.parse_command(command)
            handler = self.dispatch_table.get(parsed.type)
            
            if handler:
                handler(command)
            else:
                # Optionally log unhandled types (like UNKNOWN or FILE_SAVE)
                pass

    # --- Handlers ---

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

    def _handle_conditional(self, command: str):
        """
        Refactored logic for IF statements.
        """
        self.state_machine.register_conditional(command)
        # Check if it's an assignment-style conditional (IF x=1 y=2)
        target = self.extractor.extract_target(command)
        if target:
             self._handle_assignment(command)

    def _handle_file_match(self, command: str):
        """
        Refactored logic for MATCH FILES.
        """
        self.join_counter += 1
        sys_id = f"###SYS_JOIN_{self.join_counter}###"
        # We treat Match Files as a "System Assignment" so it appears in the graph
        self.state_machine.register_assignment(sys_id, command, dependencies=[])

    def _handle_control_flow(self, command: str):
        """
        Refactored logic for EXECUTE, SORT, etc.
        """
        self.state_machine.register_control_flow(command)

    def _handle_aggregate(self, command: str):
        """
        New Logic for AGGREGATE commands to support complexity Level 3.
        """
        # Heuristic to find targets: /target = MEAN(source)
        matches = re.findall(r"/\s*([A-Za-z0-9_]+)\s*=", command)
        
        # Extract BREAK variables as dependencies
        break_match = re.search(r"/BREAK\s*=\s*([A-Za-z0-9_\s]+)", command, re.IGNORECASE)
        deps = []
        if break_match:
            break_vars = break_match.group(1).split()
            for bv in break_vars:
                try:
                    deps.append(self.state_machine.get_current_version(bv))
                except ValueError: pass

        for target in matches:
            # Filter out keywords that might look like targets
            if target.upper() not in ["OUTFILE", "BREAK", "PRESORTED", "DOCUMENT", "MISSING"]:
                self.state_machine.register_assignment(target, command, dependencies=deps)

    # --- Utilities ---

    def analyze_dead_code(self) -> List[str]:
        raw_dead_ids = self.state_machine.find_dead_versions()
        # Filter out System Nodes so Joins aren't deleted
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