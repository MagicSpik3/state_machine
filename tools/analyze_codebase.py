import os
import ast
import sys
from collections import defaultdict
from typing import Dict, List, Set, Any

# --- Configuration ---
ROOT_DIR = "src"
OUTPUT_FILE = "codebase_atlas.md"

# --- Data Structures ---
class SymbolInfo:
    def __init__(self, name, kind, filepath, lineno, args):
        self.name = name          # Function/Class name
        self.kind = kind          # 'function' or 'method'
        self.filepath = filepath
        self.lineno = lineno
        self.args = args          # Function signature (e.g., "code: str, verbose=False")
        self.calls: Set[str] = set()       # What this symbol calls
        self.called_by: Set[str] = set()   # Who calls this symbol (Reverse Lookup)
        self.loc = 0              # Lines of Code estimate

# --- AST Analysis ---
class CodeVisitor(ast.NodeVisitor):
    def __init__(self, filepath, registry):
        self.filepath = filepath
        self.registry = registry  # Global registry of symbols
        self.current_scope = None # Track if we are inside a function/class

    def _get_signature(self, node):
        """Reconstructs the function signature text."""
        args = []
        # Positionals
        for arg in node.args.args:
            txt = arg.arg
            if arg.annotation:
                # Try to resolve type hint name
                if isinstance(arg.annotation, ast.Name):
                    txt += f": {arg.annotation.id}"
                elif isinstance(arg.annotation, ast.Attribute):
                    txt += f": {arg.annotation.attr}"
                else:
                    txt += ": ?"
            args.append(txt)
        return ", ".join(args)

    def visit_ClassDef(self, node):
        self.current_scope = node.name
        self.generic_visit(node)
        self.current_scope = None

    def visit_FunctionDef(self, node):
        # Determine name (Standalone or Class.Method)
        full_name = node.name
        kind = "function"
        if self.current_scope:
            full_name = f"{self.current_scope}.{node.name}"
            kind = "method"

        # Calculate LOC (End - Start)
        loc = (node.end_lineno - node.lineno) if hasattr(node, "end_lineno") else 0

        # Register Definition
        info = SymbolInfo(
            name=full_name,
            kind=kind,
            filepath=self.filepath,
            lineno=node.lineno,
            args=self._get_signature(node)
        )
        info.loc = loc
        self.registry[full_name] = info
        
        # Track outgoing calls within this function
        # We create a sub-visitor to scan just this function body
        call_scanner = CallScanner(full_name, self.registry)
        call_scanner.visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

class CallScanner(ast.NodeVisitor):
    """Scans inside a function to find what IT calls."""
    def __init__(self, parent_name, registry):
        self.parent_name = parent_name
        self.registry = registry

    def visit_Call(self, node):
        called_name = None
        if isinstance(node.func, ast.Name):
            called_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called_name = node.func.attr
        
        if called_name:
            # Record Outgoing Link: Parent -> Called
            # Note: We can't easily resolve "self.parser.parse" to "SpssParser.parse" statically
            # without type inference. We store the raw name "parse".
            if self.parent_name in self.registry:
                self.registry[self.parent_name].calls.add(called_name)
        
        self.generic_visit(node)

# --- Main Logic ---
def main():
    print(f"🗺️  Mapping codebase in `{ROOT_DIR}`...")
    
    # Registry: { "ClassName.method": SymbolInfo }
    registry: Dict[str, SymbolInfo] = {}

    # 1. SCANNING PASS (Build Registry & Outgoing Calls)
    files_scanned = 0
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if "__pycache__" in dirpath: continue
        
        for f in sorted(filenames):
            if not f.endswith(".py"): continue
            
            path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(path, ".")
            
            try:
                with open(path, "r", encoding="utf-8") as source:
                    tree = ast.parse(source.read())
                
                visitor = CodeVisitor(rel_path, registry)
                visitor.visit(tree)
                files_scanned += 1
            except Exception as e:
                print(f"⚠️ Error parsing {rel_path}: {e}")

    # 2. LINKING PASS (Reverse Engineering "Called By")
    # Because static analysis is fuzzy (we see 'obj.run()' but don't know 'obj' is 'RRunner'),
    # we link by simple name matching. If 'RRunner.run' exists, and someone calls '.run()', we link it.
    
    print("🔗 Linking cross-references...")
    
    # Map simple names to full qualified names for lookup
    # e.g. "run" -> ["RRunner.run", "SpssRunner.run"]
    name_lookup = defaultdict(list)
    for full_name in registry:
        short_name = full_name.split(".")[-1]
        name_lookup[short_name].append(full_name)

    for caller_name, info in registry.items():
        for called_short_name in info.calls:
            # Find who owns this short name
            possible_targets = name_lookup.get(called_short_name, [])
            for target in possible_targets:
                # Don't link recursive calls to self
                if target != caller_name:
                    registry[target].called_by.add(caller_name)

    # 3. REPORTING PASS
    print(f"📝 Generating Atlas: {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 🗺️ Codebase Atlas\n")
        f.write(f"> Index of **{len(registry)}** symbols across **{files_scanned}** files.\n\n")
        f.write("[TOC]\n\n")

        # Group by File for readability
        symbols_by_file = defaultdict(list)
        for sym in registry.values():
            symbols_by_file[sym.filepath].append(sym)

        for filepath in sorted(symbols_by_file.keys()):
            f.write(f"## 📄 `{filepath}`\n\n")
            
            # Sort symbols by line number
            file_symbols = sorted(symbols_by_file[filepath], key=lambda x: x.lineno)
            
            for sym in file_symbols:
                icon = "🏛️" if sym.kind == "function" and "." not in sym.name else "𝑓" # rough heuristic
                if sym.kind == 'method': icon = "M"
                
                # Bloat Warnings
                bloat_tags = []
                if sym.loc > 50: bloat_tags.append("🔴 **Long**")
                if len(sym.args.split(",")) > 5: bloat_tags.append("🔴 **Many Args**")
                if not sym.called_by and not sym.name.startswith("__") and "statify" not in sym.filepath:
                    bloat_tags.append("⚠️ **Orphan?**")

                tags_str = " ".join(bloat_tags)
                
                f.write(f"### {icon} `{sym.name}`\n")
                f.write(f"- **Line:** {sym.lineno} ({sym.loc} LOC) {tags_str}\n")
                f.write(f"- **Signature:** `({sym.args})`\n")
                
                # Incoming (Who calls this?)
                if sym.called_by:
                    f.write(f"- **Called By:**\n")
                    for caller in sorted(list(sym.called_by))[:5]: # Limit to 5 to avoid spam
                        f.write(f"  - `{caller}`\n")
                    if len(sym.called_by) > 5:
                        f.write(f"  - *...and {len(sym.called_by)-5} others*\n")
                else:
                    f.write(f"- **Called By:** *None detected* (Entry point?)\n")
                
                # Outgoing (What does this call?)
                if sym.calls:
                    f.write(f"- **Calls:** {', '.join(f'`{c}`' for c in sorted(list(sym.calls))[:10])}\n")
                
                f.write("\n---\n")

    print("✅ Done!")

if __name__ == "__main__":
    main()