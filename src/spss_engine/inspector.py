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
        
        # 🟢 FIX: Added 'TABLE' to capture MATCH FILES dependencies
        # Matches: /FILE='...' OR /OUTFILE='...' OR /TABLE='...'
        self._ARG_PATTERN = re.compile(r"/?(?:FILE|OUTFILE|TABLE)\s*=\s*['\"](.*?)['\"]", re.IGNORECASE)

    def scan(self, code: str) -> Tuple[List[str], List[str]]:
        inputs = []
        outputs = []
        
        commands = self.lexer.split_commands(code)
        
        for raw_cmd in commands:
            parsed = self.parser.parse_command(raw_cmd)
            
            # FILE_READ (GET DATA) and FILE_MATCH (MATCH FILES) are both Inputs
            if parsed.type == TokenType.FILE_READ or parsed.type == TokenType.FILE_MATCH:
                found = self._extract_filenames(parsed.raw)
                inputs.extend(found)
                
            elif parsed.type == TokenType.FILE_SAVE or parsed.type == TokenType.AGGREGATE:
                found = self._extract_filenames(parsed.raw)
                outputs.extend(found)
                
        return sorted(list(set(inputs))), sorted(list(set(outputs)))

    def _extract_filenames(self, command_text: str) -> List[str]:
        # Returns a list because one command (MATCH FILES) might reference multiple files
        matches = self._ARG_PATTERN.findall(command_text)
        return matches if matches else []