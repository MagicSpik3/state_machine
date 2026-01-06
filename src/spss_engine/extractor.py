import re
from typing import Optional, List


class AssignmentExtractor:
    """
    Extracts the *target* variable name from assignment commands.
    """

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().upper()

    # --- NEW: Handle "IF (Condition) Assignment" ---
    # We strip the "IF (stuff)" part and recursively check the rest.
    # This naive regex matches "IF" then greedy match until the last closing paren?
    # Actually, simpler: just remove "IF" and look for keywords later?
    # No, strictness is better.
    # Let's try matching the IF pattern, then grabbing the rest of the string.

    @staticmethod
    def extract_target(command: str) -> Optional[str]:
        cmd = command.strip()

        # Handle "IF (Condition) Assignment"
        if_match = re.match(r"^\s*IF\s*\(.+?\)\s*(.+)", cmd, re.IGNORECASE | re.DOTALL)
        if if_match:
            return AssignmentExtractor.extract_target(if_match.group(1))

        # Pattern 1: COMPUTE Target = ...
        compute_match = re.match(
            r"^\s*COMPUTE\s+([A-Za-z0-9_#@$]+)\s*=", cmd, re.IGNORECASE
        )
        if compute_match:
            return AssignmentExtractor._normalize(compute_match.group(1))

        # Pattern 2: RECODE ... INTO Target
        if "INTO" in cmd.upper():
            recode_into_match = re.search(
                r"INTO\s+([A-Za-z0-9_#@$]+)", cmd, re.IGNORECASE
            )
            if recode_into_match:
                return AssignmentExtractor._normalize(recode_into_match.group(1))

        # Pattern 3: RECODE Target (...)
        if cmd.upper().startswith("RECODE") and "INTO" not in cmd.upper():
            recode_match = re.match(
                r"^\s*RECODE\s+([A-Za-z0-9_#@$]+)", cmd, re.IGNORECASE
            )
            if recode_match:
                return AssignmentExtractor._normalize(recode_match.group(1))

        # Pattern 4: STRING/NUMERIC Target ...
        decl_match = re.match(
            r"^\s*(STRING|NUMERIC)\s+([A-Za-z0-9_#@$]+)", cmd, re.IGNORECASE
        )
        if decl_match:
            return AssignmentExtractor._normalize(decl_match.group(2))

        return None

    @staticmethod
    def extract_dependencies(expression: str) -> List[str]:
        """
        Scans a raw expression (Right-Hand Side) and returns a list of potential
        variable names found within it.
        """
        # 1. Remove string literals (e.g. 'Male') so we don't count them as vars
        # This regex removes things inside quotes.
        clean_expr = re.sub(r"('|\").*?('|\")", "", expression)

        # 2. Tokenize: Split by non-alphanumeric characters
        # We look for words that start with a letter.
        # SPSS vars can have @, #, $, _
        tokens = re.findall(r"[A-Za-z@#$][A-Za-z0-9@#$_]*", clean_expr)

        # 3. Filter Keywords (Naive list for now)
        # We don't want to list 'COMPUTE' or 'SQRT' as a dependency.
        KEYWORDS = {
            "COMPUTE",
            "IF",
            "SQRT",
            "MEAN",
            "SUM",
            "AND",
            "OR",
            "NOT",
            "EQ",
            "NE",
            "LT",
            "GT",
            "TO",
            "RECODE",
            "INTO",
            "STRING",
            "NUMERIC",
            "EXECUTE",
        }

        dependencies = []
        for token in tokens:
            normalized = token.strip().upper()
            if normalized not in KEYWORDS:
                dependencies.append(normalized)

        return list(set(dependencies))
    

    def extract_file_target(self, command: str) -> Optional[str]:
        """
        Extracts the filename from SAVE or MATCH commands.
        """
        # Simple heuristic: Look for 'file.sav' or "file.sav"
        import re
        match = re.search(r"(?:OUTFILE|TABLE|FILE)\s*=\s*['\"]([^'\"]+)['\"]", command, re.IGNORECASE)
        if match:
            return match.group(1)
        return None


    def extract_file_target(self, command: str) -> Optional[str]:
        """
        Extracts the filename from SAVE or MATCH commands.
        Looks for OUTFILE=, FILE=, or TABLE= followed by a quoted string.
        """
        # Regex explanation:
        # (?: ... )  -> Non-capturing group for the keyword options
        # \s*=\s* -> Equals sign with optional whitespace
        # ['"]       -> Opening quote (single or double)
        # ([^'"]+)   -> CAPTURE GROUP 1: Anything that isn't a quote
        # ['"]       -> Closing quote
        
        pattern = r"(?:OUTFILE|TABLE|FILE)\s*=\s*['\"]([^'\"]+)['\"]"
        
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return match.group(1)
            
        return None
