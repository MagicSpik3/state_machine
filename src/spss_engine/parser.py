from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    ASSIGNMENT = auto()
    CONDITIONAL = auto()
    FILE_SAVE = auto()   # e.g. SAVE TRANSLATE, SAVE, WRITE
    FILE_READ = auto()   # e.g. GET DATA, GET FILE, IMPORT
    FILE_MATCH = auto()  # e.g. MATCH FILES
    AGGREGATE = auto()
    CONTROL_FLOW = auto()
    UNKNOWN = auto()

@dataclass
class ParsedCommand:
    type: TokenType
    raw: str

class SpssParser:
    def parse_command(self, command: str) -> ParsedCommand:
        cmd_upper = command.strip().upper()
        
        # 1. File Inputs (Promoted Logic)
        if any(cmd_upper.startswith(k) for k in ["GET DATA", "GET FILE", "IMPORT"]):
            return ParsedCommand(TokenType.FILE_READ, command)

        # 2. File Outputs
        if cmd_upper.startswith("SAVE") or cmd_upper.startswith("WRITE"):
            return ParsedCommand(TokenType.FILE_SAVE, command)
            
        # 3. File Joins
        if cmd_upper.startswith("MATCH FILES") or cmd_upper.startswith("ADD FILES"):
            return ParsedCommand(TokenType.FILE_MATCH, command)

        if cmd_upper.startswith("AGGREGATE"):
            return ParsedCommand(TokenType.AGGREGATE, command)

        if any(cmd_upper.startswith(k) for k in ["COMPUTE", "STRING", "RECODE"]):
            return ParsedCommand(TokenType.ASSIGNMENT, command)
            
        if cmd_upper.startswith("IF") or cmd_upper.startswith("DO IF"):
            return ParsedCommand(TokenType.CONDITIONAL, command)

        # 4. Control Flow (Removed GET DATA from here)
        if any(cmd_upper.startswith(k) for k in ["EXECUTE", "SORT CASES", "FILTER", "SELECT IF", "DATA LIST"]):
            return ParsedCommand(TokenType.CONTROL_FLOW, command)

        return ParsedCommand(TokenType.UNKNOWN, command)