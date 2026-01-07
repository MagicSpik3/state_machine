import pytest
import os
from unittest.mock import MagicMock, patch
from code_forge.optimizer import CodeOptimizer
from code_forge.refiner import CodeRefiner

class TestCodeForgeTools:
    
    # --- Optimizer Tests ---
    @patch("os.path.exists")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_optimizer_linter_check(self, mock_run, mock_which, mock_exists):
        # 1. Simulate file exists
        mock_exists.return_value = True 
        
        # 2. Simulate 'lintr' is installed
        mock_which.return_value = "/usr/bin/R"
        
        # 3. FIX: Define stdout so splitlines() returns [] (No linting errors)
        # Without this, stdout is a Mock, and stdout.splitlines() is a Mock.
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        
        opt = CodeOptimizer(project_dir=".")
        result = opt.run_linter("script.R")
        
        # 4. FIX: Expect empty list (no errors), not True
        assert result == []
        assert mock_run.called

    @patch("shutil.which")
    def test_optimizer_missing_dependency(self, mock_which):
        mock_which.return_value = None # R not found
        
        opt = CodeOptimizer(project_dir=".")
        assert opt.check_dependencies() is False

    # --- Refiner Tests ---
    @patch("code_forge.refiner.OllamaClient")
    def test_refiner_flow(self, MockClientClass):
        mock_instance = MockClientClass.return_value
        mock_instance.generate.return_value = "Improved Code"
        
        refiner = CodeRefiner(mock_instance) 
        new_code = refiner.refine("Old Code")
        
        assert new_code == "Improved Code"