import os
from typing import Dict, List, Optional

class Repository:
    """
    Manages the collection of source files and their generated artifacts.
    """
    
    # FIX: Removed '.txt' so we don't accidentally scan Readmes or logs.
    VALID_EXTENSIONS = {'.spss', '.sps'}

    def __init__(self, root_path: str):
        if not os.path.exists(root_path):
            raise FileNotFoundError(f"Repository root not found: {root_path}")
            
        self.root_path = os.path.abspath(root_path)
        self._files: Dict[str, str] = {} # Key: Relative Path, Value: Content
        self._specs: Dict[str, str] = {} # Key: Relative Path, Value: Markdown Spec

    def scan(self):
        """
        Recursively finds all valid SPSS files in the root_path.
        """
        self._files.clear()
        
        for root, _, files in os.walk(self.root_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.VALID_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    
                    # Calculate relative path
                    rel_path = os.path.relpath(full_path, self.root_path)
                    
                    # Normalize to forward slashes for internal consistency
                    rel_path = rel_path.replace(os.sep, "/")
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            self._files[rel_path] = f.read()
                    except UnicodeDecodeError:
                        # Fallback for legacy encodings often found in SPSS
                        with open(full_path, 'r', encoding='latin-1') as f:
                            self._files[rel_path] = f.read()

    def list_files(self) -> List[str]:
        """Returns a list of all loaded file relative paths."""
        return sorted(list(self._files.keys()))

    def get_content(self, relative_path: str) -> Optional[str]:
        """Retrieves raw code for a specific file."""
        normalized = relative_path.replace(os.sep, "/")
        return self._files.get(normalized)

    def save_spec(self, relative_path: str, spec_content: str):
        """Stores a generated specification for a file."""
        normalized = relative_path.replace(os.sep, "/")
        if normalized not in self._files:
            raise ValueError(f"File {relative_path} does not exist in repository.")
        self._specs[normalized] = spec_content

    def get_spec(self, relative_path: str) -> Optional[str]:
        """Retrieves the generated spec."""
        normalized = relative_path.replace(os.sep, "/")
        return self._specs.get(normalized)
    

    def get_full_path(self, relative_path: str) -> str:
        """
        Reconstructs the absolute path for a given relative path.
        Useful for passing to external tools like PSPP.
        """
        # Ensure we use the correct OS separator
        native_rel_path = relative_path.replace("/", os.sep)
        return os.path.join(self.root_path, native_rel_path)    