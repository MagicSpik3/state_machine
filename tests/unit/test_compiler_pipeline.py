import pytest
from unittest.mock import patch, mock_open
from spss_engine.pipeline import CompilerPipeline

class TestCompilerPipeline:
    """
    Direct unit tests for the CompilerPipeline public API.
    Refactored [2026-01-09] to align with the Transformer/Event architecture.
    """

    def test_process_file_file_not_found(self):
        """Ensure robust error handling for missing files."""
        pipeline = CompilerPipeline()
        with pytest.raises(FileNotFoundError):
            pipeline.process_file("non_existent.spss")

    def test_process_file_success(self):
        """Verify the pipeline can ingest a file and populate state."""
        pipeline = CompilerPipeline()
        fake_content = "COMPUTE x = 1."
        
        # We mock 'open' and 'os.path.exists' to simulate a file on disk
        with patch("builtins.open", mock_open(read_data=fake_content)):
            with patch("os.path.exists", return_value=True):
                pipeline.process_file("dummy.sps")
                
        # Assertion: The state machine should now have nodes
        assert len(pipeline.state.nodes) > 0
        assert pipeline.state.nodes[0].name == "X"

    def test_analyze_dead_code_filtering(self):
        """
        Verify that analyze_dead_code() correctly identifies overwritten variables
        and filters out internal system variables.
        """
        pipeline = CompilerPipeline()
        
        # 1. Setup State: "REAL_VAR" Version 0 (Overwritten immediately)
        # We inject directly into state because we are testing the Analyzer logic,
        # not the Parser logic here.
        pipeline.state.register_assignment("REAL_VAR", "src_1", [])
        
        # 2. Setup State: "REAL_VAR" Version 1 (The active version)
        # V0 is not used here, so V0 becomes DEAD.
        pipeline.state.register_assignment("REAL_VAR", "src_2", [])
        
        # 3. Setup State: Internal System Join (Should be ignored even if dead)
        pipeline.state.register_assignment("###SYS_JOIN_1###", "sys_src", [])
        pipeline.state.register_assignment("###SYS_JOIN_1###", "sys_src_2", []) 
        
        # Execute Analysis
        dead_ids = pipeline.analyze_dead_code()
        
        # Assertion 1: REAL_VAR_0 is dead code.
        assert "REAL_VAR_0" in dead_ids
        
        # Assertion 2: The system variable (###SYS...) is filtered out.
        # It technically has a dead version, but the pipeline should hide it from the user.
        system_vars = [d for d in dead_ids if "###SYS" in d]
        assert len(system_vars) == 0