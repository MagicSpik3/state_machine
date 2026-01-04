from typing import Dict, List, NamedTuple

class VariableVersion(NamedTuple):
    id: str         # e.g. "AGE_0"
    version_idx: int # e.g. 0
    source: str     # e.g. "COMPUTE Age = 25."


class StateMachine:
    """
    Manages the Symbol Table and SSA (Static Single Assignment) versioning.
    Acts as the 'Time Machine' that tracks variable history.
    """

    def __init__(self):
        # Maps variable name (normalized) to current integer version
        self.version_counters: Dict[str, int] = {}
        
        # Maps variable name (normalized) to list of version history
        self.history_ledger: Dict[str, List[VariableVersion]] = {}

    def _normalize(self, var_name: str) -> str:
        return var_name.strip().upper()

    def register_assignment(self, var_name: str, source_code: str = "") -> str:
        """
        Records a write to a variable.
        """
        key = self._normalize(var_name)
        
        # Initialize if new
        if key not in self.version_counters:
            self.version_counters[key] = 0
            self.history_ledger[key] = []
        else:
            self.version_counters[key] += 1
            
        current_idx = self.version_counters[key]
        version_id = f"{key}_{current_idx}"
        
        # Record Provenance
        record = VariableVersion(
            id=version_id,
            version_idx=current_idx,
            source=source_code
        )
        self.history_ledger[key].append(record)
            
        return version_id

    def get_current_version(self, var_name: str) -> str:
        key = self._normalize(var_name)
        if key not in self.version_counters:
             raise ValueError(f"Variable '{var_name}' has not been defined yet.")
        return f"{key}_{self.version_counters[key]}"

    def get_history(self, var_name: str) -> List[VariableVersion]:
        """Returns the full list of changes for a specific variable."""
        key = self._normalize(var_name)
        return self.history_ledger.get(key, [])