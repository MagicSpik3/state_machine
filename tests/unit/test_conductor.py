import pytest
from spss_engine.state import StateMachine, VariableVersion
from spec_writer.conductor import Conductor

class TestConductor:
    def test_identify_islands(self):
        sm = StateMachine()
        
        # Cluster 0
        sm.register_assignment("A", "src", [])
        sm.register_assignment("B", "src", [sm.get_current_version("A")])
        
        # FIX: Manually simulate a Scope Reset to create a new cluster
        sm.reset_scope() 
        
        # Cluster 1 (The "Island")
        sm.register_assignment("X", "src", [])
        sm.register_assignment("Y", "src", [sm.get_current_version("X")])
        
        conductor = Conductor(sm)
        clusters = conductor.identify_clusters()
        
        # Now we should have 2 clusters because we called reset_scope()
        assert len(clusters) == 2
        assert "A_0" in clusters[0]
        assert "X_0" in clusters[1]

    def test_topological_sort(self):
        sm = StateMachine()
        # Tax depends on Gross
        gross = sm.register_assignment("GROSS", "src", [])
        tax = sm.register_assignment("TAX", "src", [gross])
        
        conductor = Conductor(sm)
        clusters = conductor.identify_clusters()
        sorted_nodes = conductor._topological_sort(clusters[0])
        
        # Ensure Gross comes before Tax
        assert sorted_nodes.index("GROSS_0") < sorted_nodes.index("TAX_0")