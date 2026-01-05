import re
from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    ASSIGNMENT = auto()
    CONDITIONAL = auto()
    CONTROL_FLOW = auto()  # For ELSE, END IF
    PASSTHROUGH = auto()  # For everything else


@dataclass
class ParsedStatement:
    type: TokenType
    raw: str


class SpssParser:
    """
    Classifies raw command strings into logical types using Regex.
    """

    # Regex Patterns for classification
    # We use re.IGNORECASE in the actual matching logic
    PATTERNS = [
        (TokenType.ASSIGNMENT, r"^\s*(COMPUTE|RECODE|STRING|NUMERIC)\b"),
        (TokenType.CONDITIONAL, r"^\s*(IF|DO IF)\b"),
        (TokenType.CONTROL_FLOW, r"^\s*(ELSE|END IF|EXECUTE)\b"),
    ]

    @staticmethod
    def parse_command(command: str) -> ParsedStatement:
        """
        Matches a command string against known patterns to determine its type.
        Defaults to PASSTHROUGH if no match is found.
        """
        # Iterate through patterns to find a match
        for token_type, pattern in SpssParser.PATTERNS:
            if re.match(pattern, command, re.IGNORECASE):
                return ParsedStatement(type=token_type, raw=command)

        # Default fallback
        return ParsedStatement(type=TokenType.PASSTHROUGH, raw=command)
