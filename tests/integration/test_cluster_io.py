import pytest
from spss_engine.pipeline import CompilerPipeline
from spec_writer.conductor import Conductor

class TestClusterIO:
    """
    Verifies that while variable history is reset between clusters (isolation),
    we still track which files are consumed/produced to link the clusters.
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
        # Cluster B should NOT have access to variable 'x' from Cluster A directly
        cluster_b_vars = conductor._topological_sort(clusters[1])
        assert "X_0" not in cluster_b_vars, "Variable Leakage Detected!"
        
        # 2. Verify Linkage (Zoom Out)
        # We need a new way to ask "What did Cluster A produce?" and "What did Cluster B need?"
        
        # Get metadata for the clusters
        meta_a = conductor.get_cluster_metadata(0)
        meta_b = conductor.get_cluster_metadata(1)
        
        assert "control.sav" in meta_a.outputs
        assert "control.sav" in meta_b.inputs
        
        # This proves we can reconstruct the lineage: A -> control.sav -> B