import pytest
from unittest.mock import MagicMock, patch, mock_open
from spss_engine.pipeline import CompilerPipeline

class TestCompilerPipeline:
    """
    Direct unit tests for the CompilerPipeline class methods.
    """

    def test_process_file_file_not_found(self):
        pipeline = CompilerPipeline()
        with pytest.raises(FileNotFoundError):
            pipeline.process_file("non_existent.spss")

    def test_process_file_success(self):
        pipeline = CompilerPipeline()
        fake_content = "COMPUTE x = 1."
        
        with patch("builtins.open", mock_open(read_data=fake_content)):
            with patch("os.path.exists", return_value=True):
                pipeline.process(fake_content)
                
        assert len(pipeline.state_machine.nodes) > 0

    def test_analyze_dead_code_filtering(self):
        pipeline = CompilerPipeline()
        sm = pipeline.state_machine
        
        # 1. Register "REAL_VAR" (Version 0) -> This should die
        sm.register_assignment("REAL_VAR", "src_1", [])
        
        # 2. Register "REAL_VAR" again (Version 1) -> This overwrites V0
        # Crucially, we do NOT list V0 as a dependency.
        sm.register_assignment("REAL_VAR", "src_2", [])
        
        # 3. Register System Variable -> This should be filtered out
        # Even if it's dead (unused intermediate), the pipeline should hide it.
        sm.register_assignment("###SYS_JOIN_1###", "sys_src", [])
        sm.register_assignment("###SYS_JOIN_1###", "sys_src_2", []) # Overwrite to make V0 dead
        
        dead_ids = pipeline.analyze_dead_code()
        
        # REAL_VAR_0 is intermediate and unused -> DEAD (Should appear)
        assert "REAL_VAR_0" in dead_ids
        
        # SYS_JOIN_1_0 is intermediate and unused -> DEAD (But filtered by name)
        assert "###SYS_JOIN_1###_0" not in dead_ids