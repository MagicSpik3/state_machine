from typing import List
from spss_engine.lexer import SpssLexer
from spss_engine.parser import SpssParser, TokenType
from spss_engine.extractor import AssignmentExtractor
from spss_engine.state import StateMachine

class CompilerPipeline:
    """
    Orchestrates the compilation process:
    Raw Text -> Lexer -> Parser -> Extractor -> State Machine
    """

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
                    # PASS THE RAW CODE HERE
                    self.state_machine.register_assignment(target_var, source_code=parsed.raw)
        pass # (Don't delete the real code, just representing it here)


    def process_file(self, file_path: str):
        """
        Reads a specific SPSS file and processes it.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_code = f.read()
            
        self.process(raw_code)

    def get_variable_version(self, var_name: str) -> str:
        return self.state_machine.get_current_version(var_name)
    
    def get_variable_history(self, var_name: str):
        """Exposes the history ledger from the state machine."""
        return self.state_machine.get_history(var_name)
    


    
 