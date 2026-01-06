import pytest
import os
import shutil
import json
from code_forge.optimizer import CodeOptimizer

class TestOptimizerLogic:
    
    @pytest.fixture
    def workspace(self, tmp_path):
        """Sets up a temp directory with a dummy R file."""
        test_dir = tmp_path / "temp_optimizer_test"
        test_dir.mkdir()
        
        # Create dummy R file
        r_file = test_dir / "calc_delays.R"
        r_file.write_text("dummy <- function() {}", encoding="utf-8")
        
        yield test_dir
        
        # Cleanup handled automatically by pytest tmp_path fixture

    def test_initialization(self, workspace):
        """Ensure the optimizer initializes and creates necessary artifacts."""
        optimizer = CodeOptimizer(str(workspace))
        
        # 1. Check snapshot directory creation
        assert os.path.exists(optimizer.snapshot_dir)
        assert os.path.isdir(optimizer.snapshot_dir)
        
        # 2. Check refactor script path resolution
        # We expect the optimizer to know where its internal R helper scripts are
        assert optimizer.refactor_script is not None

    def test_lint_file_detection(self, workspace):
        """Test if the optimizer can target the file."""
        optimizer = CodeOptimizer(str(workspace))
        
        # Verify it has the optimization method
        assert hasattr(optimizer, 'optimize_file')
        assert hasattr(optimizer, 'run_linter')

    def test_r_dependency_check(self, workspace):
        """
        Check if we can detect R presence. 
        (This might fail if R isn't in your path, so we handle it gracefully)
        """
        optimizer = CodeOptimizer(str(workspace))
        # This shouldn't crash
        is_available = optimizer.check_dependencies()
        assert isinstance(is_available, bool)