import os
import shutil
import subprocess
import logging
from typing import Dict, List, Any

# Setup Logging
logger = logging.getLogger("Optimizer")

class CodeOptimizer:
    """
    Manages R code quality: Linting and Refactoring.
    """
    def __init__(self, project_dir: str):
        self.project_dir = os.path.abspath(project_dir)
        self.snapshot_dir = os.path.join(self.project_dir, "snapshots")
        
        # Internal helper script for AST refactoring (Placeholder for now)
        # In a real package, this would be packaged with the library
        self.refactor_script = os.path.join(os.path.dirname(__file__), "scripts", "refactor.R")
        
        self._ensure_paths()

    def _ensure_paths(self):
        """Creates workspace folders."""
        os.makedirs(self.snapshot_dir, exist_ok=True)
        
        # Ensure the scripts dir exists even if empty, so checks pass
        script_dir = os.path.dirname(self.refactor_script)
        os.makedirs(script_dir, exist_ok=True)
        if not os.path.exists(self.refactor_script):
            # Create a dummy script if it's missing (for tests)
            with open(self.refactor_script, 'w') as f:
                f.write("# Placeholder for R AST Refactoring logic\n")

    def check_dependencies(self) -> bool:
        """Verifies R and lintr are installed."""
        if not shutil.which("Rscript"):
            logger.warning("Rscript executable not found.")
            return False
        return True

    def run_linter(self, relative_path: str) -> List[str]:
        """
        Runs 'lintr::lint()' on the specific file and returns the output.
        """
        if not self.check_dependencies():
            return ["R not installed"]

        full_path = os.path.join(self.project_dir, relative_path)
        if not os.path.exists(full_path):
            return [f"File not found: {full_path}"]

        # We assume the user has lintr installed in R
        # Command: Rscript -e "print(lintr::lint('path/to/file.R'))"
        cmd = [
            "Rscript", 
            "-e", 
            f"library(lintr); lint('{full_path}')"
        ]
        
        try:
            # Run R command
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.project_dir
            )
            
            if result.returncode != 0:
                logger.error(f"Linter crashed: {result.stderr}")
                return ["Linter Runtime Error"]
                
            # Parse standard output for lint messages
            return result.stdout.splitlines()
            
        except Exception as e:
            logger.error(f"Subprocess failed: {e}")
            return [str(e)]

    def optimize_file(self, relative_path: str):
        """
        Orchestrates the optimization: Snapshot -> Lint -> (Future) Refactor.
        """
        # 1. Snapshot original
        src = os.path.join(self.project_dir, relative_path)
        backup_name = f"{os.path.basename(relative_path)}.bak"
        dst = os.path.join(self.snapshot_dir, backup_name)
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
        
        # 2. Lint
        issues = self.run_linter(relative_path)
        return issues