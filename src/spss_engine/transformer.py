import re
from typing import List, Optional
from spss_engine.parser import ParsedCommand, TokenType
from spss_engine.events import (
    SemanticEvent, FileReadEvent, FileMatchEvent, 
    FileSaveEvent, AssignmentEvent, ScopeResetEvent
)
from spss_engine.extractor import AssignmentExtractor

class CommandTransformer:
    def __init__(self):
        self.extractor = AssignmentExtractor()
        
        # Matches: /FILE=... OR FILE=...
        # Group 1: Quoted (e.g. 'data.csv')
        # Group 2: Unquoted (e.g. mydata)
        self.re_file_arg = re.compile(r"/?(?:TABLE|FILE|OUTFILE)\s*=\s*(?:['\"]([^'\"]+)['\"]|([^\s/]+))", re.IGNORECASE)
        
        self.re_break = re.compile(r"/BREAK\s*=\s*([A-Za-z0-9_\s]+)", re.IGNORECASE)
        self.re_agg_targets = re.compile(r"/\s*([A-Za-z0-9_]+)\s*=")

    def _clean_filename(self, match) -> Optional[str]:
        """Helper to extract and clean filename from a regex match object."""
        if not match:
            return None
        
        # If Group 1 (Quoted) exists, return it as-is.
        if match.group(1):
            return match.group(1)
            
        # If Group 2 (Unquoted) exists, strip trailing dot (command terminator).
        if match.group(2):
            return match.group(2).rstrip('.')
            
        return None

    def transform(self, command: ParsedCommand) -> List[SemanticEvent]:
        events = []
        
        if command.type == TokenType.FILE_READ:
            match = self.re_file_arg.search(command.raw)
            fname = self._clean_filename(match)
            
            if fname:
                events.append(ScopeResetEvent(command.raw, reason="Destructive Load"))
                events.append(FileReadEvent(command.raw, filename=fname))

        elif command.type == TokenType.FILE_MATCH:
            files = []
            matches = self.re_file_arg.findall(command.raw)
            
            # findall returns list of tuples: [(quoted, unquoted), ...]
            for quoted, unquoted in matches:
                if quoted:
                    f = quoted
                else:
                    f = unquoted.rstrip('.') # Clean unquoted
                
                if f and f != "*": 
                    files.append(f)
            
            if files:
                events.append(FileMatchEvent(command.raw, files=files))

        elif command.type == TokenType.FILE_SAVE:
            match = self.re_file_arg.search(command.raw)
            fname = self._clean_filename(match)
            
            if fname:
                events.append(FileSaveEvent(command.raw, filename=fname))

        elif command.type in (TokenType.ASSIGNMENT, TokenType.RECODE, TokenType.CONDITIONAL):
            target = self.extractor.extract_target(command.raw)
            if target:
                raw_deps = self.extractor.extract_dependencies(command.raw)
                # Filter self-dependency
                raw_deps = [d for d in raw_deps if d.upper() != target.upper()]
                
                events.append(AssignmentEvent(
                    source_command=command.raw,
                    target=target,
                    dependencies=raw_deps,
                    expression=command.raw
                ))

        elif command.type == TokenType.AGGREGATE:
            break_match = self.re_break.search(command.raw)
            deps = break_match.group(1).split() if break_match else []
            
            targets = self.re_agg_targets.findall(command.raw)
            ignored_keywords = {"OUTFILE", "BREAK", "PRESORTED", "DOCUMENT", "MISSING"}
            
            for t in targets:
                if t.upper() not in ignored_keywords:
                    events.append(AssignmentEvent(
                        source_command=command.raw,
                        target=t,
                        dependencies=deps,
                        expression="AGGREGATE"
                    ))
            
            # Handle /OUTFILE inside AGGREGATE
            file_match = self.re_file_arg.search(command.raw)
            fname = self._clean_filename(file_match)
            
            if fname and fname != "*":
                events.append(FileSaveEvent(command.raw, filename=fname))

        return events