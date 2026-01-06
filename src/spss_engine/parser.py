import re
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    ASSIGNMENT = auto()
    CONDITIONAL = auto()
    CONTROL_FLOW = auto()  # For ELSE, END IF
    FILE_SAVE = auto()     # New: SAVE OUTFILE, SAVE TRANSLATE
    FILE_MATCH = auto()    # New: MATCH FILES
    PASSTHROUGH = auto()   # For everything else

@dataclass
class ParsedStatement:
    type: TokenType
    raw: str

class SpssParser:
    """
    Classifies raw command strings into logical types using Regex.
    """

    def __init__(self):
        # We define patterns in __init__ to allow for future extensibility
        # Order matters! Specific patterns should come before generic ones.
        self.patterns = [
            # 1. File Operations (High priority to differentiate from generic commands)
            (TokenType.FILE_SAVE,  r"^\s*SAVE\s+(TRANSLATE|OUTFILE)\b"),
            (TokenType.FILE_MATCH, r"^\s*MATCH\s+FILES\b"),
            
            # 2. Logic & Assignment
            (TokenType.ASSIGNMENT, r"^\s*(COMPUTE|RECODE|STRING|NUMERIC)\b"),
            (TokenType.CONDITIONAL, r"^\s*(IF|DO IF)\b"),
            (TokenType.CONTROL_FLOW, r"^\s*(ELSE|END IF|EXECUTE)\b"),
        ]

    def parse_command(self, command: str) -> ParsedStatement:
        """
        Matches a command string against known patterns to determine its type.
        Defaults to PASSTHROUGH if no match is found.
        """
        # Iterate through patterns to find a match
        for token_type, pattern in self.patterns:
            if re.match(pattern, command, re.IGNORECASE):
                return ParsedStatement(type=token_type, raw=command)

        # Default fallback
        return ParsedStatement(type=TokenType.PASSTHROUGH, raw=command)