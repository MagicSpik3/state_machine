import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from spss_engine.runner import PsppRunner
from code_forge.runner import RRunner

class TestRunners:
    """
    Verifies external tool execution wrappers (PSPP and R) using temporary files.
    """

    # --- PSPP Runner Tests ---
    @patch("subprocess.run")
    def test_pspp_success(self, mock_run, tmp_path):
        # 1. Setup: Create dummy SPSS file
        spss_file = tmp_path / "script.spss"
        spss_file.write_text("DATA LIST LIST /x.", encoding="utf-8")
        
        # 2. Setup: Create the expected CSV output
        # PsppRunner reads the CSV. We must ensure the file exists so the runner finds it.
        probe_csv = tmp_path / "script_probe.csv"
        # The runner typically uses DictReader, so we need Header + Data
        probe_csv.write_text("var1,var2\n10,20", encoding="utf-8")
        
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        
        runner = PsppRunner()
        
        # 3. Execute
        # Pass the directory (tmp_path) as the output_dir
        result = runner.run_and_probe(str(spss_file), str(tmp_path))
        
        # 4. Verify
        # FIX: The implementation converts keys to UPPERCASE.
        assert result.get("VAR1") == "10", f"Expected '10', got {result}"
        assert result.get("VAR2") == "20"
        
        args = mock_run.call_args[0][0]
        assert "pspp" in args

    @patch("subprocess.run")
    def test_pspp_failure(self, mock_run, tmp_path):
        spss_file = tmp_path / "script.spss"
        spss_file.write_text("FAIL ME", encoding="utf-8")
        
        # FIX: To test 'check=True', the mock must raise CalledProcessError
        error = subprocess.CalledProcessError(1, cmd=["pspp"], stderr="Syntax Error")
        mock_run.side_effect = error
        
        runner = PsppRunner()
        
        # 2. Execute & Assert
        with pytest.raises(RuntimeError) as exc:
            runner.run_and_probe(str(spss_file), str(tmp_path))
        
        assert "PSPP execution failed" in str(exc.value)

    # --- R Runner Tests ---
    @patch("subprocess.run")
    def test_r_runner_execution(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0)
        
        # 1. Setup: Create dummy R script
        r_script = tmp_path / "analysis.R"
        r_script.write_text("print('hello')", encoding="utf-8")
        
        # Initialize with script path
        runner = RRunner(str(r_script))
        
        # 2. Execution
        # FIX: The implementation does NOT take an output path argument.
        # It takes optional input_vars. We call it with defaults.
        
        # We assume the runner will try to read 'r_output.csv'.
        # We mock pandas to avoid needing that file to exist physically or have valid content.
        with patch("pandas.read_csv") as mock_read:
             mock_df = MagicMock()
             # Mock the 'iloc[-1]' call to return a row
             mock_row = MagicMock()
             # When iterating the row, we want columns.
             # But the implementation iterates df.columns.
             mock_df.empty = False
             mock_df.columns = ["col1"]
             mock_df.iloc.__getitem__.return_value = {"col1": 100.0}
             
             mock_read.return_value = mock_df
             
             runner.run_and_capture()

        # 3. Verify
        assert mock_run.called
        args = mock_run.call_args[0][0]
        
        # FIX: Assert that the wrapper is being executed
        # The implementation runs: ["Rscript", wrapper_path]
        assert "Rscript" == args[0]
        assert "run_wrapper.R" in args[1]
        
        # Optional: Verify the wrapper content was written correctly
        wrapper_path = tmp_path / "run_wrapper.R"
        assert wrapper_path.exists()
        content = wrapper_path.read_text()
        # The wrapper should 'source' our analysis script
        assert f'source("analysis.R")' in content