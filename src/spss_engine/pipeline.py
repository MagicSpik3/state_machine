from typing import List
import os
from spss_engine.lexer import SpssLexer
from spss_engine.parser import SpssParser, TokenType
from spss_engine.extractor import AssignmentExtractor
from spss_engine.state import StateMachine


class CompilerPipeline:
    def __init__(self):
        self.state_machine = StateMachine()

    def process(self, raw_code: str):
        lexer = SpssLexer(raw_code)
        commands = lexer.get_commands()

        for cmd in commands:
            parsed = SpssParser.parse_command(cmd)

            if parsed.type in (TokenType.ASSIGNMENT, TokenType.CONDITIONAL):
                target_var = AssignmentExtractor.extract_target(parsed.raw)

                if target_var:
                    # 1. Find potential dependencies in the raw string
                    # Extract Dependencies from the FULL command line
                    # (Ideally we only scan the RHS, but scanning the whole line is a safe heuristic for now)
                    raw_deps = AssignmentExtractor.extract_dependencies(parsed.raw)

                    # 2. Resolve them to actual SSA versions (e.g. "GROSS" -> "GROSS_0")
                    # 2. Remove the target var itself from dependencies (to avoid self-reference loops in simple assignments)
                    # e.g. COMPUTE x = x + 1. We might want self-reference here?
                    # Let's keep it simple: if it's on the RHS, it's a dependency.
                    # But extract_dependencies scans the whole string, so it will find the Target.
                    # We should remove the Target from the list.
                    resolved_deps = []
                    for dep_name in raw_deps:
                        if dep_name == target_var:
                            continue  # Don't depend on yourself in the same line for now

                        try:
                            # Try to find the CURRENT version of this dependency
                            current_ver = self.state_machine.get_current_version(
                                dep_name
                            )
                            resolved_deps.append(current_ver)
                        except ValueError:
                            # Variable hasn't been defined yet (or is a keyword/noise we missed)
                            # We skip it for now.
                            pass

                    # 3. Register with resolved dependencies
                    self.state_machine.register_assignment(
                        target_var, source_code=parsed.raw, dependencies=resolved_deps
                    )

    def analyze_dead_code(self) -> List[str]:
        """Returns a list of variable version IDs (e.g. 'X_0') that are unused."""
        return self.state_machine.find_dead_versions()

    def process_file(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            self.process(f.read())

    def get_variable_version(self, var_name: str) -> str:
        return self.state_machine.get_current_version(var_name)

    def get_variable_history(self, var_name: str):
        return self.state_machine.get_history(var_name)
