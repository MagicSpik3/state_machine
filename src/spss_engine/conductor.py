from typing import List, Dict, Set
from collections import defaultdict, deque
from spss_engine.state import StateMachine

class Conductor:
    """
    Organizes the flat list of variables into logical 'Chapters' (Clusters)
    based on the topology of the dependency graph.
    """
    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine
        
        # Build Adjacency List (Undirected for clustering, Directed for sorting)
        self.adj_undirected = defaultdict(set)
        self.adj_directed = defaultdict(set)
        self.in_degree = defaultdict(int)
        self.all_nodes = set()
        
        self._build_graph()

    def _build_graph(self):
        for var_name, history in self.state_machine.history_ledger.items():
            for version in history:
                u = version.id
                self.all_nodes.add(u)
                
                # Ensure node exists in dicts
                if u not in self.adj_directed: self.adj_directed[u] = set()
                if u not in self.in_degree: self.in_degree[u] = 0
                
                for v in version.dependencies:
                    # Edge: v (dependency) -> u (current)
                    self.all_nodes.add(v)
                    
                    # Directed: v -> u
                    self.adj_directed[v].add(u)
                    self.in_degree[u] += 1
                    
                    # Undirected: v <-> u
                    self.adj_undirected[u].add(v)
                    self.adj_undirected[v].add(u)

    def identify_clusters(self) -> List[List[str]]:
        """
        Returns a list of clusters. Each cluster is a list of Node IDs.
        Uses Weakly Connected Components (BFS).
        """
        visited = set()
        clusters = []
        
        # Sort nodes for deterministic starting points
        sorted_nodes = sorted(list(self.all_nodes))
        
        for node in sorted_nodes:
            if node not in visited:
                # Start a new cluster
                cluster_nodes = self._bfs_cluster(node, visited)
                
                # Sort the cluster Topologically (Logic Order)
                sorted_cluster = self._topological_sort(cluster_nodes)
                clusters.append(sorted_cluster)
                
        return clusters

    def _bfs_cluster(self, start_node: str, visited: Set[str]) -> Set[str]:
        """Finds all nodes connected to start_node (Undirected)."""
        cluster = set()
        queue = deque([start_node])
        visited.add(start_node)
        cluster.add(start_node)
        
        while queue:
            u = queue.popleft()
            for v in self.adj_undirected[u]:
                if v not in visited:
                    visited.add(v)
                    cluster.add(v)
                    queue.append(v)
        return cluster

    def _topological_sort(self, cluster_nodes: Set[str]) -> List[str]:
        """
        Sorts nodes such that dependencies come before dependents.
        Uses Kahn's Algorithm restricted to the subgraph.
        """
        # 1. Calculate local in-degrees for the subgraph
        local_in_degree = {u: 0 for u in cluster_nodes}
        for u in cluster_nodes:
            for v in self.adj_directed[u]:
                if v in cluster_nodes:
                    local_in_degree[v] += 1
                    
        # 2. Initialize Queue with nodes having 0 dependencies (within cluster)
        queue = deque([u for u in cluster_nodes if local_in_degree[u] == 0])
        sorted_list = []
        
        while queue:
            u = queue.popleft()
            sorted_list.append(u)
            
            for v in self.adj_directed[u]:
                if v in cluster_nodes:
                    local_in_degree[v] -= 1
                    if local_in_degree[v] == 0:
                        queue.append(v)
                        
        # Handle cycles (if any nodes remain) or disconnected stragglers
        if len(sorted_list) != len(cluster_nodes):
            # If cycles exist, just append the remaining nodes arbitrarily
            remaining = cluster_nodes - set(sorted_list)
            sorted_list.extend(sorted(list(remaining)))
            
        return sorted_list