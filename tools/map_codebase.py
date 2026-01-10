#map_codebase.py
import os
import ast
import sys

def get_imports(tree):
    """Extracts imports from the AST."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(f"import {n.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for n in node.names:
                imports.append(f"from {module} import {n.name}")
    return sorted(list(set(imports)))

def get_structure(tree):
    """Extracts Classes and Functions."""
    structure = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            structure.append({
                "type": "class",
                "name": node.name,
                "methods": methods
            })
        elif isinstance(node, ast.FunctionDef):
            structure.append({
                "type": "function",
                "name": node.name
            })
    return structure

def analyze_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        return None, None

    imports = get_imports(tree)
    structure = get_structure(tree)
    return imports, structure

def main():
    root_dir = "src"
    print(f"# 🗺️ Codebase Architecture Map")
    print(f"**Root:** `{os.path.abspath(root_dir)}`\n")

    for dirpath, _, filenames in os.walk(root_dir):
        # Skip pycache
        if "__pycache__" in dirpath:
            continue
            
        py_files = [f for f in filenames if f.endswith(".py")]
        if not py_files:
            continue

        # Print Package Header
        rel_path = os.path.relpath(dirpath, ".")
        print(f"## 📦 Package: `{rel_path}`")
        
        for file in sorted(py_files):
            full_path = os.path.join(dirpath, file)
            imports, structure = analyze_file(full_path)
            
            if imports is None: continue # Skip errors
            
            print(f"\n### 📄 `{file}`")
            
            if imports:
                print("**Imports:**")
                for imp in imports:
                    print(f"- `{imp}`")
            
            if structure:
                print("\n**Definitions:**")
                for item in structure:
                    if item["type"] == "class":
                        print(f"- 🏛️ **Class** `{item['name']}`")
                        for method in item["methods"]:
                            print(f"    - `def {method}(...)`")
                    elif item["type"] == "function":
                        print(f"- 𝑓 **Func** `{item['name']}(...)`")
            
            print("\n---")

if __name__ == "__main__":
    main()