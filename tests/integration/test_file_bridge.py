import pytest
from spss_engine.pipeline import CompilerPipeline

class TestFileBridge:
    def test_save_and_match_connection(self):
        """
        Scenario:
        1. Calculate X.
        2. Save X to a file.
        3. Load (Match) that file.
        4. Use X to calculate Y.
        
        Expectation: Y should depend on X.
        """
        code = """
        COMPUTE X = 100.
        SAVE OUTFILE='temp_data.sav'.
        
        * Clear state effectively (simulated by new context in real usage, 
        * but here we just want to see the link).
        
        MATCH FILES /FILE=* /TABLE='temp_data.sav'.
        COMPUTE Y = X * 2.
        """
        
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        # We want to trace Y back to X.
        # Current behavior: Y depends on X_1 (from MATCH), but X_1 has no parent.
        # Desired behavior: X_1 (from MATCH) depends on X_0 (from COMPUTE/SAVE).
        
        # Get history of Y
        y_ver = pipeline.get_variable_version("Y") # Y_0
        
        # Check dependencies
        assert "X" in str(y_ver.dependencies) # This usually passes (Y depends on 'some' X)
        
        # The Critical Test: Graph Connectivity
        # We need to find the specific version of X that Y depends on, 
        # and see if THAT version links back to the original computation.
        
        # Let's inspect the graph edges directly
        # We expect: COMPUTE X -> SAVE -> MATCH -> COMPUTE Y
        
        # For now, let's just assert that we detect the file operations
        # This will fail until we implement the parser logic
        match_nodes = [v for k, hist in pipeline.state.history_ledger.items() for v in hist if "MATCH FILES" in v.source]
        assert len(match_nodes) > 0, "Parser failed to detect MATCH FILES as a state event"