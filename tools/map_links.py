import os
import ast
import sys
from collections import defaultdict

# --- AST Analysis Tools ---

class CallVisitor(ast.NodeVisitor):
    """
    Visits functions and methods to track what they call.
    """
    def __init__(self):
        self.calls = [] # List of strings identifying called functions

    def visit_Call(self, node):
        call_name = self._get_func_name(node.func)
        if call_name:
            self.calls.append(call_name)
        self.generic_visit(node)

    def _get_func_name(self, node):
        """Recursively resolves names like 'self.parser.parse'."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_func_name(node.value)
            return f"{value}.{node.attr}" if value else node.attr
        elif isinstance(node, ast.Call):
            # Handle chained calls like func()()
            return self._get_func_name(node.func)
        return None

def get_function_calls(tree):
    """
    Extracts the call graph from a file's AST.
    Returns a structure:
    [
        {
            "context": "class MyClass",
            "method": "my_method",
            "calls": ["print", "self.helper"]
        },
        ...
    ]
    """
    links = []

    for node in tree.body:
        # 1. Standalone Functions
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            visitor = CallVisitor()
            visitor.visit(node)
            links.append({
                "type": "function",
                "name": node.name,
                "calls": visitor.calls
            })
        
        # 2. Classes and Methods
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                    visitor = CallVisitor()
                    visitor.visit(item)
                    links.append({
                        "type": "method",
                        "context": node.name,
                        "name": item.name,
                        "calls": visitor.calls
                    })
    return links

def analyze_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        return get_function_calls(tree)
    except Exception:
        return None

# --- Report Generation ---

def main():
    root_dir = "src"
    print(f"# 🔗 Codebase Call Graph")
    print(f"**Root:** `{os.path.abspath(root_dir)}`\n")
    print("> ➡️ Indicates a function call made by the definition.\n")

    for dirpath, _, filenames in os.walk(root_dir):
        if "__pycache__" in dirpath: continue
        
        py_files = [f for f in filenames if f.endswith(".py")]
        if not py_files: continue

        rel_path = os.path.relpath(dirpath, ".")
        print(f"## 📦 Package: `{rel_path}`")
        
        for file in sorted(py_files):
            full_path = os.path.join(dirpath, file)
            links = analyze_file(full_path)
            
            if not links: continue
            
            print(f"\n### 📄 `{file}`")
            
            # Group by class context for cleaner output
            current_class = None
            
            for item in links:
                # Handle grouping visuals
                if item['type'] == 'method':
                    if item['context'] != current_class:
                        print(f"- 🏛️ **Class** `{item['context']}`")
                        current_class = item['context']
                    indent = "    "
                    prefix = "def"
                else:
                    current_class = None
                    indent = ""
                    prefix = "𝑓 **func**"

                # Print Definition
                print(f"{indent}- {prefix} `{item['name']}`")
                
                # Print Calls (Deduplicated but ordered)
                unique_calls = []
                seen = set()
                for call in item['calls']:
                    if call not in seen:
                        unique_calls.append(call)
                        seen.add(call)

                if unique_calls:
                    for call in unique_calls:
                        # Highlight internal vs external calls visually
                        icon = "➡️"
                        if call.startswith("self."):
                            icon = "🔄" # Internal call
                        elif "." in call:
                            icon = "ex" # External/Module call (likely)
                            
                        # Markdown formatting for the flow
                        print(f"{indent}    - {icon} `{call}`")
                else:
                    print(f"{indent}    - *No outgoing calls detected*")

            print("\n---")

if __name__ == "__main__":
    main()