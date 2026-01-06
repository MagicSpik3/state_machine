import pytest
import os
import shutil
from spss_engine.repository import Repository

class TestRepository:

    @pytest.fixture
    def repo_structure(self, tmp_path):
        """
        Creates a temporary dummy repo structure:
        /repo
           /main.spss
           /subdir
               /module.sps
               /ignore_me.txt
        """
        root = tmp_path / "repo"
        root.mkdir()
        (root / "main.spss").write_text("COMPUTE X=1.")
        
        subdir = root / "subdir"
        subdir.mkdir()
        (subdir / "module.sps").write_text("COMPUTE Y=2.")
        (subdir / "ignore_me.txt").write_text("I am not code.")
        
        return str(root)

    def test_scan_files(self, repo_structure):
        """
        Ensure the repo finds only valid SPSS files recursively.
        """
        repo = Repository(repo_structure)
        repo.scan()
        
        files = repo.list_files()
        
        # Should find main.spss and module.sps
        assert len(files) == 2
        
        # Check relative paths (platform independent)
        assert "main.spss" in files
        # Depending on OS, might be subdir/module.sps or subdir\module.sps
        # We normalize to forward slashes in the implementation usually
        normalized_files = [f.replace(os.sep, "/") for f in files]
        assert "subdir/module.sps" in normalized_files

    def test_get_content(self, repo_structure):
        """
        Ensure we can read the file content.
        """
        repo = Repository(repo_structure)
        repo.scan()
        
        content = repo.get_content("main.spss")
        assert content == "COMPUTE X=1."
        
        # Test missing file
        assert repo.get_content("ghost.spss") is None

    def test_save_and_get_spec(self, repo_structure):
        """
        Ensure we can store the generated markdown spec in memory.
        """
        repo = Repository(repo_structure)
        repo.scan()
        
        spec_text = "# Spec for Main"
        repo.save_spec("main.spss", spec_text)
        
        assert repo.get_spec("main.spss") == spec_text
        assert repo.get_spec("subdir/module.sps") is None

    def test_file_not_found_error(self):
        """
        Repo should handle non-existent roots gracefully (or raise error).
        """
        with pytest.raises(FileNotFoundError):
            Repository("/path/to/nowhere")