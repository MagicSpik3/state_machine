from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class VariableVersion:
    id: str               # e.g., "AGE_0"
    source: str           # e.g., "COMPUTE Age = 25."
    dependencies: List[str] = field(default_factory=list) # e.g., ["DOB_0"]

class StateMachine:
    """
    Tracks the lifecycle of variables (SSA) and manages the Symbol Table.
    """
    def __init__(self):
        self.symbol_table: Dict[str, int] = {}  # Map: "AGE" -> 0 (Current Index)
        self.history_ledger: Dict[str, List[VariableVersion]] = {} # Map: "AGE" -> [AGE_0, AGE_1]
        
        # BRIDGE LOGIC: Tracks file snapshots
        self.file_registry: Dict[str, List[str]] = {} # Map: "file.sav" -> ["AGE_0", "STATUS_1"]

    def _normalize(self, var_name: str) -> str:
        return var_name.strip().upper()

    def get_current_version(self, var_name: str) -> str:
        """Returns the ID of the current active version (e.g., 'AGE_1')."""
        norm_name = self._normalize(var_name)
        if norm_name not in self.symbol_table:
            raise ValueError(f"Variable {var_name} is not defined.")
        idx = self.symbol_table[norm_name]
        return f"{norm_name}_{idx}"

    def get_history(self, var_name: str) -> List[VariableVersion]:
        norm_name = self._normalize(var_name)
        return self.history_ledger.get(norm_name, [])

    def register_assignment(self, target: str, source_code: str, dependencies: List[str] = None):
        """
        Creates a new SSA version for the target variable.
        """
        if dependencies is None:
            dependencies = []
            
        norm_target = self._normalize(target)
        
        # Increment version index (SSA)
        if norm_target not in self.symbol_table:
            self.symbol_table[norm_target] = 0
        else:
            self.symbol_table[norm_target] += 1
            
        idx = self.symbol_table[norm_target]
        version_id = f"{norm_target}_{idx}"
        
        # Record history
        new_version = VariableVersion(id=version_id, source=source_code, dependencies=dependencies)
        
        if norm_target not in self.history_ledger:
            self.history_ledger[norm_target] = []
        self.history_ledger[norm_target].append(new_version)

    # --- CONTROL FLOW HANDLERS ---
    # Currently we treat these as markers, but eventually they will handle Phi functions.
    
    def register_conditional(self, source_code: str):
        """
        Registers a branching event (IF / DO IF).
        For now, this is a placeholder to prevent the Pipeline from crashing.
        In Phase 8, this will trigger a Stack Push.
        """
        pass 

    def register_control_flow(self, source_code: str):
        """
        Registers flow changes (ELSE, END IF, EXECUTE).
        """
        pass

    # --- FILE BRIDGE HANDLERS (New) ---

    def register_file_save(self, filename: str, source_code: str):
        """
        Snapshots the current symbol table into a file registry.
        """
        # Store the current version ID of every active variable
        current_snapshot = []
        for var, idx in self.symbol_table.items():
            current_snapshot.append(f"{var}_{idx}")
        
        self.file_registry[filename] = current_snapshot

    def register_file_match(self, filename: str, source_code: str):
        """
        Simulates loading a file by linking current variables to the snapshot versions.
        """
        if filename in self.file_registry:
            snapshot_versions = self.file_registry[filename]
            
            for upstream_id in snapshot_versions:
                # upstream_id looks like "AGE_0"
                # We want to create a NEW version "AGE_1" that depends on "AGE_0"
                # This creates the visible bridge in the graph.
                
                var_name = upstream_id.rsplit('_', 1)[0]
                
                self.register_assignment(
                    target=var_name,
                    source_code=f"MATCH FILES from '{filename}'",
                    dependencies=[upstream_id]
                )

    # --- ANALYSIS ---

    def find_dead_versions(self) -> List[str]:
        """
        Identifies versions that are never used as a dependency for any subsequent version.
        Excludes the 'Current' (final) version of any variable.
        """
        used_dependencies = set()
        
        # 1. Collect all used dependencies
        for history in self.history_ledger.values():
            for version in history:
                for dep in version.dependencies:
                    used_dependencies.add(dep)
        
        dead_versions = []
        
        # 2. Check each version
        for var_name, history in self.history_ledger.items():
            current_idx = self.symbol_table[var_name]
            current_id = f"{var_name}_{current_idx}"
            
            for version in history:
                # A version is DEAD if:
                # 1. It is NOT in the used set
                # 2. It is NOT the final current state (which is implicitly "used" by the output)
                if version.id not in used_dependencies and version.id != current_id:
                    dead_versions.append(version.id)
                    
        return dead_versions