import re
from typing import Optional

class AssignmentExtractor:
    """
    Extracts the *target* variable name from assignment commands.
    """
    
    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().upper()

    @staticmethod
    def extract_target(command: str) -> Optional[str]:
        cmd = command.strip()
        
        # --- NEW: Handle "IF (Condition) Assignment" ---
        # We strip the "IF (stuff)" part and recursively check the rest.
        # This naive regex matches "IF" then greedy match until the last closing paren? 
        # Actually, simpler: just remove "IF" and look for keywords later? 
        # No, strictness is better. 
        # Let's try matching the IF pattern, then grabbing the rest of the string.
        
        if_match = re.match(r"^\s*IF\s*\(.+?\)\s*(.+)", cmd, re.IGNORECASE | re.DOTALL)
        if if_match:
            # The "rest" of the command (e.g. "RECODE Status ...")
            inner_cmd = if_match.group(1)
            # Recursively extract from the inner command
            return AssignmentExtractor.extract_target(inner_cmd)
        # -----------------------------------------------

        # Pattern 1: COMPUTE Target = ...
        compute_match = re.match(r"^\s*COMPUTE\s+([A-Za-z0-9_#@$]+)\s*=", cmd, re.IGNORECASE)
        if compute_match:
            return AssignmentExtractor._normalize(compute_match.group(1))

        # Pattern 2: RECODE ... INTO Target
        if "INTO" in cmd.upper():
            recode_into_match = re.search(r"INTO\s+([A-Za-z0-9_#@$]+)", cmd, re.IGNORECASE)
            if recode_into_match:
                return AssignmentExtractor._normalize(recode_into_match.group(1))

        # Pattern 3: RECODE Target (...) -- In-place recode
        if cmd.upper().startswith("RECODE") and "INTO" not in cmd.upper():
            recode_match = re.match(r"^\s*RECODE\s+([A-Za-z0-9_#@$]+)", cmd, re.IGNORECASE)
            if recode_match:
                return AssignmentExtractor._normalize(recode_match.group(1))

        # Pattern 4: STRING/NUMERIC Target ...
        decl_match = re.match(r"^\s*(STRING|NUMERIC)\s+([A-Za-z0-9_#@$]+)", cmd, re.IGNORECASE)
        if decl_match:
            return AssignmentExtractor._normalize(decl_match.group(2))

        return None