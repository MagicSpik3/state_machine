from typing import List, Dict, Set, Optional
from spss_engine.state import StateMachine, VariableVersion, ClusterMetadata

class Conductor:
    """
    Analyzes the State Machine to organize logic into Clusters.
    """
    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine

    def identify_clusters(self) -> List[List[str]]:
        """
        Groups nodes by their explicit cluster_index.
        Returns a list of lists, where each inner list contains Node IDs.
        """
        # Initialize buckets based on how many clusters we actually tracked
        num_clusters = self.state_machine.current_cluster_index + 1
        buckets = [[] for _ in range(num_clusters)]
        
        for node in self.state_machine.nodes:
            # Safety check (though register_assignment guarantees valid index)
            idx = node.cluster_index
            if 0 <= idx < num_clusters:
                buckets[idx].append(node.id)
                
        # Filter out empty buckets if needed (e.g., if a cluster only had control flow but no vars)
        # But for indexing consistency with metadata, we usually keep them.
        return buckets

    def _topological_sort(self, cluster_node_ids: List[str]) -> List[str]:
        """
        Sorts nodes within a cluster for readability.
        (Simple implementation: preserves creation order which is usually correct for SPSS)
        """
        # Since self.state_machine.nodes is already chronological, 
        # and the buckets are filled in that order, they are already sorted.
        return cluster_node_ids

    def get_cluster_metadata(self, cluster_index: int) -> Optional[ClusterMetadata]:
        if 0 <= cluster_index < len(self.state_machine.clusters):
            return self.state_machine.clusters[cluster_index]
        return None