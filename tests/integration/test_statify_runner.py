import pytest
from unittest.mock import MagicMock, patch, mock_open
from statify import process_file
import os

class TestStatifyRunner:
    
    @patch('statify.RRunner')
    @patch('statify.RGenerator')
    @patch('statify.CodeRefiner')
    @patch('statify.SpecGenerator')
    @patch('statify.GraphGenerator')
    @patch('statify.PsppRunner')
    @patch('statify.CompilerPipeline')
    @patch('statify.shutil.which') # Mock which to ensure PSPP is "found"
    @patch('builtins.open', new_callable=mock_open, read_data="COMPUTE x=1.") # Mock file reading
    @patch('statify.os.makedirs') # Mock directory creation
    def test_process_file_flow_control(self, mock_makedirs, mock_file, mock_which, MockPipeline, MockPspp, MockGraph, MockSpec, MockRefiner, MockGen, MockRunner):
        """
        Tests that r_path is correctly passed from Generator to Runner.
        """
        # 1. Ensure PSPP is "found" so verification logic runs
        mock_which.return_value = "/usr/bin/pspp"

        # 2. Setup Mocks for Pipeline and PSPP
        mock_pipeline_instance = MockPipeline.return_value
        mock_pipeline_instance.state_machine.history_ledger = {"VAR": []}
        mock_pipeline_instance.analyze_dead_code.return_value = []

        # Return some data so the "Equivalence Check" block triggers
        MockPspp.return_value.run_and_probe.return_value = {"VAR": 100}
        
        # 3. Setup Generator
        mock_gen_instance = MockGen.return_value
        mock_gen_instance.generate_script.return_value = "print('hello')"
        
        # 4. Setup Runner
        mock_runner_instance = MockRunner.return_value
        mock_runner_instance.run_and_capture.return_value = {"VAR": 100}
        
        # 5. Execute with CORRECT Arguments
        process_file(
            full_path="dummy.sps",
            relative_path="dummy.sps",
            output_root="out",
            model="test_model",
            generate_code=True,
            refine_mode=True
        )
        
        # 6. Verification
        # Ensure Generator was called
        assert MockGen.called
        
        # Ensure Runner was called (This confirms flow control reached step 7)
        assert MockRunner.called
        
        # Verify r_path was passed to Runner (it should end in .R)
        args, _ = MockRunner.call_args
        assert args[0].endswith(".R")