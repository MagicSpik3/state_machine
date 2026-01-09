import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from spss_engine.spss_runner import PsppRunner


class TestPSPPRunner:
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
