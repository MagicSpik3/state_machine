import pytest
from spss_engine.pipeline import CompilerPipeline
from spec_writer.conductor import Conductor

class TestClusterIO:
    """
    Verifies that the State Machine correctly tracks file I/O to link clusters,
    even when variable history is reset for isolation.
    """
    
    def test_cluster_linkage(self):
        code = """
        * CLUSTER A: Produce the Control File.
        GET DATA /FILE='raw_control.csv'.
        COMPUTE x = 1.
        SAVE OUTFILE='control.sav'.

        * CLUSTER B: Consume the Control File.
        GET DATA /FILE='raw_data.csv'.
        MATCH FILES /FILE=* /TABLE='control.sav' /BY id.
        SAVE OUTFILE='final.sav'.
        """
        
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        conductor = Conductor(pipeline.state_machine)
        clusters = conductor.identify_clusters()
        
        # 1. Verify Isolation (Zoom In)
        # Cluster B (index 1) should NOT have access to variable 'X_0' from Cluster A
        # because GET DATA should have triggered a scope reset.
        cluster_b_vars = conductor._topological_sort(clusters[1])
        assert "X_0" not in cluster_b_vars, "Variable Leakage Detected! Scope did not reset."
        
        # 2. Verify Linkage (Zoom Out)
        # We check the Metadata on the State Machine to see if it captured the file flow.
        meta_a = conductor.get_cluster_metadata(0)
        meta_b = conductor.get_cluster_metadata(1)
        
        # Debugging print if assertion fails
        print(f"Cluster A Outputs: {meta_a.outputs}")
        print(f"Cluster B Inputs: {meta_b.inputs}")

        assert "control.sav" in meta_a.outputs, "Cluster A failed to record output file."
        assert "control.sav" in meta_b.inputs, "Cluster B failed to record input file."