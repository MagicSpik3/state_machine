import pytest
from unittest.mock import patch, MagicMock
from spss_engine.spss_runner import PsppRunner
from code_forge.runner import RRunner

class TestRunners:
    
    @patch("subprocess.run")
    def test_pspp_success(self, mock_run, tmp_path):
        # Setup
        spss_file = tmp_path / "script.spss"
        spss_file.write_text("DATA LIST LIST /x.", encoding="utf-8")
        
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        
        runner = PsppRunner()
        
        # FIX: Unpack the tuple (data, artifacts)
        data, artifacts = runner.run_and_probe(str(spss_file), str(tmp_path))
        
        # Use assertion on the dictionary 'data'
        assert isinstance(data, dict)
        assert isinstance(artifacts, list)

    @patch("subprocess.run")
    def test_r_runner_execution(self, mock_run, tmp_path):
        # Setup
        r_script = tmp_path / "analysis.R"
        r_script.write_text("print('hello')", encoding="utf-8")
        
        mock_run.return_value = MagicMock(returncode=0)
        
        runner = RRunner(str(r_script))
        
        # Mock pandas reading the output
        with patch("pandas.read_csv") as mock_read:
             mock_df = MagicMock()
             mock_df.empty = False
             mock_df.iloc.__getitem__.return_value = {"col": "val"}
             # iloc[0].to_dict() chain
             mock_df.iloc = [MagicMock(to_dict=lambda: {"col": "val"})]
             
             mock_read.return_value = mock_df
             
             # Action
             result = runner.run_and_capture()

        assert mock_run.called
        assert isinstance(result, dict)