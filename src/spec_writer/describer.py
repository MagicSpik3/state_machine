from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

@dataclass(frozen=True)
class VariableVersion:
    name: str
    version: int
    
    @property
    def id(self) -> str:
        return f"{self.name}_{self.version}"

@dataclass
class ClusterMetadata:
    id: str
    nodes: List[str]
    description: str = "Logic Sequence"

class StateMachine:
    """
    Manages the lifecycle of variables and the logic graph.
    """
    def __init__(self):
        self.variables: Dict[str, int] = {}  # name -> current_version
        self.graph = nx.DiGraph()
        self.scope_stack: List[Set[str]] = [set()]
        
        # Track cluster membership
        self.clusters: Dict[str, List[str]] = {} 

    def get_current_version(self, var_name: str) -> VariableVersion:
        """Returns the latest version of a variable."""
        version = self.variables.get(var_name, 0)
        return VariableVersion(var_name, version)

    # --- MISSING METHOD FIX ---
    def get_var_by_id(self, node_id: str) -> VariableVersion:
        """
        Retrieves the VariableVersion object associated with a graph node.
        """
        if node_id not in self.graph.nodes:
             # Fallback for error handling or untracked nodes
             name = node_id.split('_')[0]
             return VariableVersion(name, 0)
             
        node_data = self.graph.nodes[node_id]
        # We expect the 'variable' key to hold the VariableVersion object
        # If not found, reconstruct it from ID
        if 'variable' in node_data:
            return node_data['variable']
        
        # Fallback reconstruction
        parts = node_id.rsplit('_', 1)
        name = parts[0]
        version = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return VariableVersion(name, version)
    # --------------------------

    def register_assignment(self, var_name: str, source_code: str, dependencies: List[str] = None):
        if dependencies is None:
            dependencies = []
            
        # 1. Create new version
        current_ver = self.variables.get(var_name, 0)
        new_ver = current_ver + 1
        self.variables[var_name] = new_ver
        
        new_var = VariableVersion(var_name, new_ver)
        
        # 2. Add to Graph
        self.graph.add_node(
            new_var.id, 
            type="assignment", 
            source=source_code,
            variable=new_var,  # Storing the object here
            cluster=self._get_current_cluster()
        )
        
        # 3. Add Edges (Dependencies)
        for dep_name in dependencies:
            dep_ver = self.get_current_version(dep_name)
            if dep_ver.id in self.graph.nodes:
                self.graph.add_edge(dep_ver.id, new_var.id)
                
        return new_var

    def _get_current_cluster(self) -> str:
        # Simplified clustering logic placeholder
        return "default"