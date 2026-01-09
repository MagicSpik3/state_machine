import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from code_forge.R_runner import RRunner
from spss_engine.state import StateMachine, VariableVersion

class TestRRunner:
    """
    Verifies external tool execution wrappers (PSPP and R) using temporary files.
    """
    # --- Existing Basic Test ---
    @patch("subprocess.run")
    def test_r_runner_execution(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0)
        
        # 1. Setup: Create dummy R script
        r_script = tmp_path / "analysis.R"
        r_script.write_text("print('hello')", encoding="utf-8")
        
        runner = RRunner(str(r_script))
        
        # 2. Execution & Mocking
        with patch("pandas.read_csv") as mock_read:
             mock_df = MagicMock()
             mock_df.empty = False
             mock_df.columns = ["col1"]
             mock_df.iloc.__getitem__.return_value = {"col1": 100.0}
             mock_read.return_value = mock_df
             
             runner.run_and_capture()

        # 3. Verify Basic Execution
        assert mock_run.called
        args = mock_run.call_args[0][0]
        assert "Rscript" == args[0]
        assert "run_wrapper.R" in args[1]

    # --- 🟢 NEW TEST: Input Discovery & Mocking ---
    @patch("subprocess.run")
    def test_input_discovery_and_mocking(self, mock_run, tmp_path):
        """
        Verifies that if a StateMachine is provided, the runner scans for 
        missing inputs (dependencies) and initializes them in the R wrapper.
        """
        mock_run.return_value = MagicMock(returncode=0)
        r_script = tmp_path / "bmi_logic.R"
        r_script.write_text("# Logic goes here", encoding="utf-8")

        # 1. Setup Mock State Machine
        # Scenario: 'BMI' exists, but depends on 'weight' and 'height'.
        # 'weight' and 'height' are NOT in .nodes, so they are inputs.
        
        mock_state = MagicMock(spec=StateMachine)
        
        # Create dependencies (Inputs)
        # Note: We use the real class or a robust mock that has .name
        dep_weight = VariableVersion(name="WEIGHT", version=0, source="")
        dep_height = VariableVersion(name="HEIGHT", version=0, source="")
        
        # Create the Output Node
        node_bmi = VariableVersion(
            name="BMI", 
            version=1, 
            source="COMPUTE BMI...", 
            dependencies=[dep_weight, dep_height]
        )
        
        # The StateMachine only 'owns' the logic nodes, not the raw inputs
        mock_state.nodes = [node_bmi]

        # 2. Initialize Runner with State Machine
        runner = RRunner(str(r_script), state_machine=mock_state)

        # 3. Execute (without providing explicit inputs)
        with patch("pandas.read_csv") as mock_read:
             mock_df = MagicMock()
             mock_df.empty = True # We don't care about output for this test
             mock_read.return_value = mock_df
             
             runner.run_and_capture() # Should trigger auto-discovery

        # 4. Verify the Wrapper Content
        # We need to check if 'weight = 1' and 'height = 1' were written to the file.
        wrapper_path = tmp_path / "run_wrapper.R"
        assert wrapper_path.exists()
        
        content = wrapper_path.read_text()

        # ... inside test_input_discovery_and_mocking ...
        content = wrapper_path.read_text()
        assert "df <- data.frame" in content
        assert "weight = 1" in content
        assert "height = 1" in content
        assert "source" in content        