import os
import ast
from collections import defaultdict

# --- Configuration ---
# Names to ignore (Magic methods, common overrides, etc.)
IGNORE_LIST = {
    "__init__", "__str__", "__repr__", "__call__", "__enter__", "__exit__",
    "setUp", "tearDown", "process", "transform", "scan", "run" # Common interface names often called dynamically or implicitly
}

# Directories to scan for definitions and usages
# Was: SOURCE_DIRS = ["src", "tests"]
SOURCE_DIRS = ["src"]
ROOT_FILES = ["statify.py"]

class ReferenceVisitor(ast.NodeVisitor):
    """
    Scans a file for EVERY identifier usage.
    If a name is used anywhere (variable, function call, attribute), it's considered 'alive'.
    """
    def __init__(self):
        self.references = set()

    def visit_Name(self, node):
        self.references.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.references.add(node.attr)
        self.generic_visit(node)
        
    def visit_Call(self, node):
        # We explicitly check calls to capture things like func_name()
        if isinstance(node.func, ast.Name):
            self.references.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.references.add(node.func.attr)
        self.generic_visit(node)

def get_definitions_and_references(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
    except Exception:
        return [], set()

    # 1. Find Definitions (The Candidates)
    definitions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name not in IGNORE_LIST and not node.name.startswith("__"):
                definitions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "type": "def"
                })
        # We generally track Class definitions too, but usually tracking methods is more useful for dead code
        elif isinstance(node, ast.ClassDef):
             definitions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "type": "class"
                })

    # 2. Find References (The Proof of Life)
    visitor = ReferenceVisitor()
    visitor.visit(tree)
    
    # We remove the definitions themselves from the references count 
    # (defining a function doesn't count as using it)
    # However, for recursion, a function might call itself.
    # The Name-Based Heuristic is simple: is this name used ANYWHERE else?
    
    return definitions, visitor.references

def main():
    print(f"# 💀 Dead Code Detector")
    print(f"**Scanning:** `{', '.join(SOURCE_DIRS)}` + root files\n")

    # Master Registry
    all_definitions = defaultdict(list) # name -> list of (filepath, lineno)
    all_references = set()

    # 1. SCANNING PHASE
    files_to_scan = []
    
    # Add Root Files
    for f in ROOT_FILES:
        if os.path.exists(f): files_to_scan.append(f)

    # Add Source Dirs
    for d in SOURCE_DIRS:
        for dirpath, _, filenames in os.walk(d):
            if "__pycache__" in dirpath: continue
            for f in filenames:
                if f.endswith(".py"):
                    files_to_scan.append(os.path.join(dirpath, f))

    print(f"Scanning {len(files_to_scan)} files...")

    for filepath in files_to_scan:
        defs, refs = get_definitions_and_references(filepath)
        
        # Store definitions mapped by filename
        for d in defs:
            all_definitions[filepath].append(d)
        
        # Aggregate all references globally
        all_references.update(refs)

    # 2. ANALYSIS PHASE
    print("\n## 🔍 Potential Dead Code Analysis")
    print("> **Note:** This uses a name-based heuristic. If a method is named `run`, and `run` is called anywhere, it is considered alive.")
    print("> Items listed below have **ZERO** references found in the codebase (excluding their own definition).\n")

    dead_count = 0
    
    for filepath, defs in all_definitions.items():
        file_dead = []
        for d in defs:
            name = d['name']
            
            # THE CHECK: Is this name used anywhere?
            # We have to be careful: the definition itself adds to the 'references' count in some AST parsers depending on scope.
            # But our Visitor is global.
            
            # If the name exists in references, we check if it appears *enough*.
            # Actually, simply checking membership in `all_references` is tricky because the definition file ITSELF 
            # might use it recursively, or the parser might pick up the definition line as a Name node.
            
            # Robust Check: 
            # We assume 'all_references' contains every usage.
            # If I define `def my_unused_func():`, 'my_unused_func' is in definitions.
            # Does 'my_unused_func' appear in `all_references`? 
            # Yes, because the `def` statement uses the name.
            
            # So, we need to count occurrences, or rely on the fact that `ReferenceVisitor` 
            # visits `Name`, `Attribute`, and `Call`. 
            # Standard `def` name is NOT visited by `visit_Name`, it's an attribute of `FunctionDef`.
            # So if `ReferenceVisitor` finds it, it's a usage!
            
            if name not in all_references:
                file_dead.append(d)

        if file_dead:
            print(f"### 📄 `{filepath}`")
            for item in file_dead:
                dead_count += 1
                icon = "📦" if item['type'] == 'class' else "𝑓"
                print(f"- {icon} **{item['name']}** (Line {item['lineno']})")
            print("")

    if dead_count == 0:
        print("✅ **No dead code detected!** (Or everything is named commonly enough to pass the filter)")
    else:
        print(f"---")
        print(f"**Found {dead_count} potential zombies.** 🧟")

if __name__ == "__main__":
    main()