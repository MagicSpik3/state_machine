from typing import Dict

class StateMachine:
    """
    Manages the Symbol Table and SSA (Static Single Assignment) versioning.
    Acts as the 'Time Machine' that tracks variable history.
    """

    def __init__(self):
        # Maps variable name (normalized upper case) to current integer version
        # e.g. {"AGE": 0, "INCOME": 2}
        self.version_counters: Dict[str, int] = {}

    def _normalize(self, var_name: str) -> str:
        """SPSS is case-insensitive. Normalize to uppercase."""
        return var_name.strip().upper()

    def register_assignment(self, var_name: str) -> str:
        """
        Records a write to a variable.
        - If new, initializes at version 0.
        - If exists, increments version (SSA).
        Returns the new unique identifier (e.g., 'AGE_1').
        """
        key = self._normalize(var_name)
        
        if key not in self.version_counters:
            self.version_counters[key] = 0
        else:
            self.version_counters[key] += 1
            
        return f"{key}_{self.version_counters[key]}"

    def get_current_version(self, var_name: str) -> str:
        """
        Returns the current active version identifier for a variable.
        Raises KeyError if variable is unknown (or returns None, depending on preference).
        """
        key = self._normalize(var_name)
        if key not in self.version_counters:
             raise ValueError(f"Variable '{var_name}' has not been defined yet.")
             
        return f"{key}_{self.version_counters[key]}"