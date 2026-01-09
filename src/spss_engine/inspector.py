import re
import logging
from typing import List, Tuple
from spss_engine.lexer import SpssLexer
from spss_engine.parser import SpssParser, TokenType

logger = logging.getLogger("SourceInspector")

class SourceInspector:
    def __init__(self):
        self.lexer = SpssLexer()
        self.parser = SpssParser()
        
        # FIX: Added '?' after slash to make it optional.
        # Matches: /FILE='...' OR FILE='...'
        self._ARG_PATTERN = re.compile(r"/?(?:FILE|OUTFILE)\s*=\s*['\"](.*?)['\"]", re.IGNORECASE)

    def scan(self, code: str) -> Tuple[List[str], List[str]]:
        inputs = []
        outputs = []
        
        commands = self.lexer.split_commands(code)
        
        for raw_cmd in commands:
            parsed = self.parser.parse_command(raw_cmd)
            
            if parsed.type == TokenType.FILE_READ or parsed.type == TokenType.FILE_MATCH:
                found = self._extract_filename(parsed.raw)
                if found: inputs.append(found)
                
            elif parsed.type == TokenType.FILE_SAVE:
                found = self._extract_filename(parsed.raw)
                if found: outputs.append(found)
                
        return sorted(list(set(inputs))), sorted(list(set(outputs)))

    def _extract_filename(self, command_text: str) -> str:
        matches = self._ARG_PATTERN.findall(command_text)
        if matches:
            return matches[0]
        return None