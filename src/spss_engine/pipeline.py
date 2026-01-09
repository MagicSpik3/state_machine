# src/spss_engine/pipeline.py
from spss_engine.extractor import AssignmentExtractor
from spss_engine.lexer import SpssLexer
from spss_engine.parser import SpssParser, TokenType
from spss_engine.state import StateMachine, VariableVersion
from spss_engine.transformer import CommandTransformer
from spss_engine.events import (
    SemanticEvent, FileReadEvent, FileMatchEvent, 
    FileSaveEvent, AssignmentEvent, ScopeResetEvent
)
from typing import List, Optional
import os


class CompilerPipeline:
    def __init__(self):
        self.state = StateMachine()
        self.parser = SpssParser()
        self.lexer = SpssLexer()
        self.transformer = CommandTransformer()
        self.extractor = AssignmentExtractor() 
        
        self.source_file = "script.sps"
        self.join_counter = 0

 
    def process(self, code: str):
        commands = self.lexer.split_commands(code)
        
        for cmd_text in commands:
            normalized = self.lexer.normalize_command(cmd_text)
            parsed = self.parser.parse_command(normalized)
            events = self.transformer.transform(parsed)
            
            for event in events:
                self._apply_event(event)

    def _apply_event(self, event: SemanticEvent):
        if isinstance(event, ScopeResetEvent):
            if self.state._get_current_cluster().node_count > 0:
                self.state.reset_scope()

        elif isinstance(event, FileReadEvent):
            self.state.register_input_file(event.filename)

        elif isinstance(event, FileSaveEvent):
            self.state.register_output_file(event.filename)
            self.state.register_control_flow(event.source_command)

        elif isinstance(event, FileMatchEvent):
            for f in event.files:
                self.state.register_input_file(f)
            self.join_counter += 1
            sys_id = f"###SYS_JOIN_{self.join_counter}###"
            self.state.register_assignment(sys_id, event.source_command, [])

        elif isinstance(event, AssignmentEvent):
            resolved_deps = []
            for dep_name in event.dependencies:
                try:
                    ver = self.state.get_current_version(dep_name)
                    resolved_deps.append(ver)
                except ValueError:
                    pass 

            self.state.register_assignment(
                var_name=event.target,
                source=event.source_command,
                dependencies=resolved_deps
            )
            
            if event.source_command.upper().startswith("IF"):
                self.state.register_conditional(event.source_command)

    # 🟢 RESTORED: API Methods needed by tests
    def get_variable_version(self, var_name: str) -> Optional[VariableVersion]:
        try:
            return self.state.get_current_version(var_name)
        except ValueError:
            return None

    def get_variable_history(self, var_name: str) -> List[VariableVersion]:
        return self.state.get_history(var_name)

    def analyze_dead_code(self) -> List[str]:
        raw_dead_ids = self.state.find_dead_versions()
        return [vid for vid in raw_dead_ids if "###SYS_" not in vid]

    def process_file(self, file_path: str):
        if not os.path.exists(file_path): 
            raise FileNotFoundError(f"Source file not found: {file_path}")
        self.source_file = file_path # Capture path
        with open(file_path, "r", encoding="utf-8") as f: 
            self.process(f.read())