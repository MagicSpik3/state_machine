from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    ASSIGNMENT = auto()
    CONDITIONAL = auto()
    FILE_READ = auto()
    FILE_MATCH = auto()
    FILE_SAVE = auto()
    CONTROL_FLOW = auto()
    AGGREGATE = auto()
    RECODE = auto()       # 🟢 ADDED THIS
    UNKNOWN = auto()

@dataclass
class ParsedCommand:
    type: TokenType
    raw: str

class SpssParser:
    def parse_command(self, command: str) -> ParsedCommand:
        cmd_upper = command.strip().upper()
        
        # 🟢 ADD RECODE DETECTION
        if cmd_upper.startswith("RECODE"):
            return ParsedCommand(TokenType.RECODE, command)
            
        if cmd_upper.startswith("COMPUTE") or cmd_upper.startswith("STRING"):
            return ParsedCommand(TokenType.ASSIGNMENT, command)
            
        if cmd_upper.startswith("IF"):
            return ParsedCommand(TokenType.CONDITIONAL, command)
            
        if any(cmd_upper.startswith(x) for x in ["GET DATA", "GET FILE"]):
            return ParsedCommand(TokenType.FILE_READ, command)
            
        if cmd_upper.startswith("MATCH FILES") or cmd_upper.startswith("ADD FILES"):
            return ParsedCommand(TokenType.FILE_MATCH, command)
            
        if cmd_upper.startswith("SAVE") or cmd_upper.startswith("SAVE TRANSLATE"):
            return ParsedCommand(TokenType.FILE_SAVE, command)
            
        if cmd_upper.startswith("AGGREGATE"):
            return ParsedCommand(TokenType.AGGREGATE, command)
            
        if any(cmd_upper.startswith(x) for x in ["SORT CASES", "EXECUTE", "DATASET"]):
            return ParsedCommand(TokenType.CONTROL_FLOW, command)
            
        return ParsedCommand(TokenType.UNKNOWN, command)