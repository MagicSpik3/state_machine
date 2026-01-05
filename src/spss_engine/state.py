from typing import Dict, List, NamedTuple, Optional


class VariableVersion(NamedTuple):
    id: str  # e.g. "AGE_0"
    version_idx: int  # e.g. 0
    source: str  # e.g. "COMPUTE Age = 25."
    dependencies: List[str] = []


class StateMachine:
    """
    Manages the Symbol Table and SSA (Static Single Assignment) versioning.
    """

    def __init__(self):
        self.version_counters: Dict[str, int] = {}
        self.history_ledger: Dict[str, List[VariableVersion]] = {}

    def _normalize(self, var_name: str) -> str:
        return var_name.strip().upper()

    def register_assignment(
        self, var_name: str, source_code: str = "", dependencies: List[str] = None
    ) -> str:
        """
        Records a write to a variable.
        """
        if dependencies is None:
            dependencies = []

        key = self._normalize(var_name)

        if key not in self.version_counters:
            self.version_counters[key] = 0
            self.history_ledger[key] = []
        else:
            self.version_counters[key] += 1

        current_idx = self.version_counters[key]
        version_id = f"{key}_{current_idx}"

        # Record Provenance AND Dependencies
        record = VariableVersion(
            id=version_id,
            version_idx=current_idx,
            source=source_code,
            dependencies=dependencies,
        )
        self.history_ledger[key].append(record)

        return version_id

    def get_current_version(self, var_name: str) -> str:
        key = self._normalize(var_name)
        if key not in self.version_counters:
            raise ValueError(f"Variable '{var_name}' has not been defined yet.")
        return f"{key}_{self.version_counters[key]}"

    def get_history(self, var_name: str) -> List[VariableVersion]:
        key = self._normalize(var_name)
        return self.history_ledger.get(key, [])

    def find_dead_versions(self) -> List[str]:
        """
        Identifies variable versions that were created but never read by any subsequent logic,
        and are not the final state of the variable.
        """
        # 1. Collect all dependencies that ARE used
        used_versions = set()

        for var_history in self.history_ledger.values():
            for version in var_history:
                for dep in version.dependencies:
                    used_versions.add(dep)

        dead_list = []

        # 2. Check every version to see if it's used or final
        for var_name, history in self.history_ledger.items():
            current_active_version = self.get_current_version(var_name)

            for version in history:
                # Rule 1: If it's the final version, it's implicitly used (by the resulting dataset)
                if version.id == current_active_version:
                    continue

                # Rule 2: If it appears in someone else's dependency list, it's used
                if version.id in used_versions:
                    continue

                # Otherwise, it's dead code.
                dead_list.append(version.id)

        return dead_list
