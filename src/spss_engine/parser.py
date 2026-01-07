from enum import Enum, auto
import re
import logging
from typing import List, Optional
from dataclasses import dataclass
from spss_engine.state import StateMachine

logger = logging.getLogger("Parser")

class TokenType(Enum):
    ASSIGNMENT = auto()
    CONDITIONAL = auto()
    FILE_SAVE = auto()
    FILE_MATCH = auto()
    AGGREGATE = auto()   # <--- NEW: Support for Aggregation
    CONTROL_FLOW = auto()
    UNKNOWN = auto()

@dataclass
class ParsedCommand:
    type: TokenType
    original: str

class SpssParser:
    def parse_command(self, command: str) -> ParsedCommand:
        cmd_upper = command.strip().upper()
        
        if cmd_upper.startswith("MATCH FILES"):
            return ParsedCommand(TokenType.FILE_MATCH, command)

        if cmd_upper.startswith("AGGREGATE"): # <--- NEW
            return ParsedCommand(TokenType.AGGREGATE, command)

        if any(cmd_upper.startswith(k) for k in ["COMPUTE", "STRING", "RECODE"]):
            return ParsedCommand(TokenType.ASSIGNMENT, command)
            
        if cmd_upper.startswith("IF"):
            return ParsedCommand(TokenType.CONDITIONAL, command)
            
        if cmd_upper.startswith("SAVE OUTFILE") or cmd_upper.startswith("SAVE TRANSLATE"):
            return ParsedCommand(TokenType.FILE_SAVE, command)

        if any(cmd_upper.startswith(k) for k in ["EXECUTE", "SORT CASES", "FILTER", "GET DATA", "SELECT IF"]):
            return ParsedCommand(TokenType.CONTROL_FLOW, command)

        return ParsedCommand(TokenType.UNKNOWN, command)    