import os
import ast
import networkx as nx
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
# Methods to completely ignore (Noise filter)
IGNORE_METHODS = {
    # Python Built-ins
    'append', 'extend', 'join', 'split', 'strip', 'rstrip', 'lstrip', 
    'upper', 'lower', 'startswith', 'endswith', 'replace', 'format',
    'keys', 'values', 'items', 'get', 'update', 'pop', 'remove', 'add',
    'read', 'write', 'close', 'open', 'print', 'len', 'str', 'int', 
    'list', 'dict', 'set', 'enumerate', 'range', 'zip', 'map', 'filter',
    'super', 'isinstance', 'hasattr', 'getattr', 'setattr',
    # Common Logging/System
    'info', 'warning', 'error', 'debug', 'exception', 'log',
    'exists', 'join', 'dirname', 'abspath', 'basename',
    # Generic Helpers
    '__init__', '__str__', '__repr__'
}

# --- 1. The Scanner ---
class CallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        # Extract the name of the function being called
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)

def analyze_file_deps(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception:
        return []

    edges = []
    
    for node in tree.body:
        # Detect Class Methods (The high-level architecture)
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    caller = f"{class_name}" # Collapse method calls to Class-level relationships
                    # Alternatively: caller = f"{class_name}.{item.name}" (Granular)
                    
                    visitor = CallVisitor()
                    visitor.visit(item)
                    for callee in visitor.calls:
                        if callee not in IGNORE_METHODS:
                            edges.append((caller, callee))
                            
        # Detect Standalone Functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            caller = node.name
            visitor = CallVisitor()
            visitor.visit(node)
            for callee in visitor.calls:
                if callee not in IGNORE_METHODS:
                    edges.append((caller, callee))

    return edges

# --- 2. The Brain ---
def build_graph(root_dir):
    G = nx.DiGraph()
    print(f"🕵️  Scanning {root_dir} (Filtering noise)...")
    
    for dirpath, _, filenames in os.walk(root_dir):
        if "__pycache__" in dirpath: continue
        
        for file in filenames:
            if not file.endswith(".py"): continue
            filepath = os.path.join(dirpath, file)
            
            edges = analyze_file_deps(filepath)
            for caller, callee in edges:
                # Only add if it looks like an internal class (PascalCase) or known module
                # This is a heuristic to filter out 'json.load' type calls if we want stricter views
                G.add_edge(caller, callee)

    return G

# --- 3. The Artist ---
def draw_graph(G):
    # Remove nodes with Degree 0 (Isolated files)
    G.remove_nodes_from(list(nx.isolates(G)))
    
    # Remove Self-Loops (Class calls its own methods)
    G.remove_edges_from(nx.selfloop_edges(G))

    print(f"🎨 Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    
    # Sizing based on Degree Centrality (Importance)
    d = dict(G.degree)
    node_sizes = [v * 50 + 200 for v in d.values()]
    
    # Coloring based on role (Source vs Sink)
    node_colors = []
    for node in G.nodes():
        if G.out_degree(node) > G.in_degree(node):
            node_colors.append("lightgreen") # Orchestrator / Caller
        else:
            node_colors.append("skyblue")    # Service / Callee

    # Layout
    pos = nx.spring_layout(G, k=0.3, iterations=50) # Increased 'k' pushes nodes apart
    
    plt.figure(figsize=(16, 12))
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, edgecolors='black', linewidths=1, alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.4, arrowsize=15, edge_color="gray")
    
    # Draw labels only for significant nodes
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")
    
    plt.title("Refined Architecture Map (Classes & Logic)")
    plt.axis("off")
    plt.savefig("architecture_map_refined.png", dpi=300)
    print("✅ Saved: architecture_map_refined.png")

if __name__ == "__main__":
    G = build_graph("src")
    draw_graph(G)