import logging
from enum import Enum, auto
from dataclasses import dataclass

logger = logging.getLogger("Parser")

class TokenType(Enum):
    ASSIGNMENT = auto()
    CONDITIONAL = auto()
    FILE_SAVE = auto()
    FILE_MATCH = auto()
    CONTROL_FLOW = auto()
    UNKNOWN = auto()
    # Note: PASSTHROUGH is removed as per new architecture, tests must update.

@dataclass
class ParsedCommand:
    type: TokenType
    original: str
    
    # Backward compatibility for tests expecting .raw
    @property
    def raw(self):
        return self.original

class SpssParser:
    def parse_command(self, command: str) -> ParsedCommand:
        cmd_upper = command.strip().upper()
        
        # 1. MATCH FILES
        if cmd_upper.startswith("MATCH FILES"):
            return ParsedCommand(TokenType.FILE_MATCH, command)

        # 2. Assignments (COMPUTE, STRING, RECODE) <--- ADDED RECODE
        if any(cmd_upper.startswith(k) for k in ["COMPUTE", "STRING", "RECODE"]):
            return ParsedCommand(TokenType.ASSIGNMENT, command)
            
        # 3. Conditionals (IF)
        if cmd_upper.startswith("IF"):
            return ParsedCommand(TokenType.CONDITIONAL, command)
            
        # 4. File Save (SAVE OUTFILE)
        if cmd_upper.startswith("SAVE OUTFILE"):
            return ParsedCommand(TokenType.FILE_SAVE, command)

        # 5. Control Flow
        if any(cmd_upper.startswith(k) for k in ["EXECUTE", "SORT CASES", "FILTER"]):
            return ParsedCommand(TokenType.CONTROL_FLOW, command)

        return ParsedCommand(TokenType.UNKNOWN, command)