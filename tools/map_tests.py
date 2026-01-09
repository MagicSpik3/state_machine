#map_tests.py
import os
import ast
import sys
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set

# --- Analysis Core ---

def get_ast_nodes(tree):
    """Extracts flat list of Classes and Functions from AST."""
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            nodes.append({
                "type": "class",
                "name": node.name,
                "methods": methods,
                "lineno": node.lineno
            })
        elif isinstance(node, ast.FunctionDef):
            nodes.append({
                "type": "function",
                "name": node.name,
                "lineno": node.lineno
            })
    return nodes

def analyze_file(filepath):
    """Parses a file and returns its structure."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception:
        return None
    return get_ast_nodes(tree)

# --- Test Mapping Logic ---

class CodebaseMapper:
    def __init__(self, src_root="src", test_root="tests"):
        self.src_root = src_root
        self.test_root = test_root
        # Map: target_name (lower) -> List of test locations
        self.test_registry = defaultdict(list)
        
    def scan_tests(self):
        """Builds a registry of all available tests."""
        print(f"🕵️  Scanning tests in `{self.test_root}`...")
        for dirpath, _, filenames in os.walk(self.test_root):
            for file in filenames:
                if not file.endswith(".py") or not file.startswith("test_"):
                    continue
                
                full_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(full_path, ".")
                nodes = analyze_file(full_path)
                
                if not nodes: continue

                for node in nodes:
                    name = node['name']
                    # Store strict mapping
                    self.test_registry[name.lower()].append(f"{rel_path}::{name}")
                    
                    # Store loose mapping (strip 'Test' prefix)
                    if name.lower().startswith("test"):
                        stripped = name[4:].lower()
                        if stripped.startswith("_"): stripped = stripped[1:]
                        if stripped:
                            self.test_registry[stripped].append(f"{rel_path}::{name}")

    def find_tests_for(self, name: str) -> List[str]:
        """Finds tests that likely cover the given class/function name."""
        name_lower = name.lower()

        # 1. MANUAL MAPPINGS (The "Truth Source")
        # Explicitly link components to their grouped test suites
        manual_mappings = {
            # Runners -> TestRunners
            "rrunner": ["tests/unit/test_runners.py::TestRunners"],
            "pspprunner": ["tests/unit/test_runners.py::TestRunners"],
            
            # Data Structures -> TestDataStructures
            "variableversion": ["tests/unit/test_data_structures.py::TestDataStructures"],
            "clustermetadata": ["tests/unit/test_data_structures.py::TestDataStructures"],
            "parsedcommand": ["tests/unit/test_data_structures.py::TestDataStructures"],
            "tokentype": ["tests/unit/test_data_structures.py::TestDataStructures"],
            
            # Code Forge Tools -> TestCodeForgeTools
            "codeoptimizer": ["tests/unit/test_code_forge_tools.py::TestCodeForgeTools"],
            "coderefiner": ["tests/unit/test_code_forge_tools.py::TestCodeForgeTools"],
        }
        
        if name_lower in manual_mappings:
            return manual_mappings[name_lower]

        # 2. Heuristic Match
        return sorted(list(set(self.test_registry.get(name_lower, []))))

    def generate_report(self):
        self.scan_tests()
        
        print(f"\n# 🗺️ Codebase Functionality Map")
        print(f"**Root:** `{os.path.abspath(self.src_root)}`\n")

        total_components = 0
        tested_components = 0

        for dirpath, _, filenames in os.walk(self.src_root):
            if "__pycache__" in dirpath: continue
            
            py_files = [f for f in filenames if f.endswith(".py") and f != "__init__.py"]
            if not py_files: continue

            rel_pkg = os.path.relpath(dirpath, ".")
            print(f"## 📦 Package: `{rel_pkg}`")
            
            for file in sorted(py_files):
                full_path = os.path.join(dirpath, file)
                structure = analyze_file(full_path)
                
                if not structure: continue
                
                print(f"\n### 📄 `{file}`")
                
                for item in structure:
                    total_components += 1
                    name = item['name']
                    item_type = item['type']
                    icon = "🏛️" if item_type == "class" else "𝑓"
                    
                    tests = self.find_tests_for(name)
                    
                    if tests:
                        status = "✅"
                        tested_components += 1
                        test_str = f" <span style='color:green'>Found {len(tests)} test(s)</span>"
                    else:
                        status = "⚠️"
                        test_str = " <span style='color:orange'>**UNTESTED**</span>"

                    print(f"- {status} {icon} **{name}** {test_str}")
                    for t in tests:
                        print(f"    - 🧪 `{t}`")
                        
                    if item_type == "class":
                        method_names = [m for m in item["methods"] if not m.startswith("__")]
                        if method_names:
                            print(f"    - *Methods:* {', '.join(method_names)}")

            print("\n---")
            
        if total_components > 0:
            coverage = (tested_components / total_components) * 100
            print(f"\n## 📊 Summary")
            print(f"**Coverage:** {coverage:.1f}% ({tested_components}/{total_components} components linked to tests)")

def main():
    mapper = CodebaseMapper()
    mapper.generate_report()

if __name__ == "__main__":
    main()