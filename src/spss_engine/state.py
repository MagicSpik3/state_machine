from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

@dataclass
class VariableVersion:
    name: str
    version: int
    source: str 
    dependencies: List['VariableVersion'] = field(default_factory=list)
    cluster_index: int = 0
    
    @property
    def id(self):
        return f"{self.name}_{self.version}"

    # 🟢 ADD THIS METHOD
    def __str__(self):
        return self.id

@dataclass
class ClusterMetadata:
    index: int
    inputs: Set[str] = field(default_factory=set)
    outputs: Set[str] = field(default_factory=set)
    node_count: int = 0 

class StateMachine:
    def __init__(self):
        self.history_ledger: Dict[str, List[VariableVersion]] = {}
        self.nodes: List[VariableVersion] = []
        self.conditionals: List[str] = []
        self.control_flow: List[str] = []
        
        self.clusters: List[ClusterMetadata] = [ClusterMetadata(index=0)]
        self.current_cluster_index = 0

    def get_history(self, var_name: str) -> List[VariableVersion]:
        return self.history_ledger.get(var_name.upper(), [])

    def get_current_version(self, var_name: str) -> VariableVersion:
        history = self.get_history(var_name)
        if not history:
            raise ValueError(f"Variable {var_name} not found in history.")
        return history[-1]

    def register_assignment(self, var_name: str, source: str, dependencies: List[VariableVersion] = None):
        if dependencies is None: dependencies = []
            
        var_upper = var_name.upper()
        history = self.get_history(var_upper)
        new_version_num = len(history)
        
        new_node = VariableVersion(
            name=var_upper, 
            version=new_version_num, 
            source=source, 
            dependencies=dependencies,
            cluster_index=self.current_cluster_index 
        )
        
        if var_upper not in self.history_ledger:
            self.history_ledger[var_upper] = []
            
        self.history_ledger[var_upper].append(new_node)
        self.nodes.append(new_node)
        self._get_current_cluster().node_count += 1
        return new_node

    def register_conditional(self, command: str):
        self.conditionals.append(command)

    def register_control_flow(self, command: str):
        self.control_flow.append(command)
        
    def find_dead_versions(self) -> List[str]:
        usage_map = {node.id: 0 for node in self.nodes}
        for node in self.nodes:
            for dep in node.dependencies:
                usage_map[dep.id] += 1
        dead_ids = []
        for var_name, history in self.history_ledger.items():
            for i, ver in enumerate(history):
                if i == len(history) - 1: continue
                if usage_map[ver.id] == 0: dead_ids.append(ver.id)
        return dead_ids

    def _get_current_cluster(self) -> ClusterMetadata:
        return self.clusters[self.current_cluster_index]

    def register_input_file(self, filename: str):
        clean_name = filename.strip("'").strip('"').strip()
        if clean_name: self._get_current_cluster().inputs.add(clean_name)

    def register_output_file(self, filename: str):
        clean_name = filename.strip("'").strip('"').strip()
        if clean_name: self._get_current_cluster().outputs.add(clean_name)

    def reset_scope(self):
        """
        Finalizes the current cluster and starts a new one.
        PREVENTS EMPTY CLUSTERS: If the current cluster is pristine (unused),
        we do not advance the index.
        """
        current = self._get_current_cluster()
        
        # Check if pristine: No nodes, No inputs, No outputs
        is_pristine = (current.node_count == 0) and \
                      (len(current.inputs) == 0) and \
                      (len(current.outputs) == 0)
                      
        self.history_ledger.clear()
        
        if is_pristine:
            # We are at the start of the script (or repeated resets). 
            # Stay on the current cluster.
            return

        self.current_cluster_index += 1
        self.clusters.append(ClusterMetadata(index=self.current_cluster_index))