# Engineering Log

## Current Architecture
**Pattern:** State Machine / Decompiler
**Goal:** Parse SPSS code into a Control Flow Graph (CFG) and Static Single Assignment (SSA) form to ensure deterministic auditing of business logic.

## Decision Journal

### [2024-05-20] Pivot to State Machine Architecture
**Reason:** The previous "Evolution Engine" (LLM-based translation) was non-deterministic and hard to verify. We moved to a "compiler-style" approach where Python models the logic state mathematically.
**Action:** - Created `src/spss_engine` as the new core.
- **DEPRECATED:** The entire `core/` directory (EvolutionEngine, SpecWriter, etc.) and `experiments/` from the previous iteration.
- **STATUS:** These old files should be archived or deleted to prevent confusion.

### [2024-05-20] Lexer Implementation
**Reason:** Need a robust way to handle SPSS "dot termination" logic before parsing.
**Design:** `SpssLexer` class using splitlines and aggregation. 
**Constraint:** Must handle dots inside quoted strings correctly (e.g., `COMPUTE x = "End."`).

## Active File Manifest
| File | Responsibility | Test File |
|------|---------------|-----------|
| `src/spss_engine/lexer.py` | Tokenizes raw text into command strings. | `tests/unit/test_lexer.py` |
| `ENGINEERING_LOG.md` | Tracks architectural decisions. | N/A |

### [2026-01-04] Lexer Verification & Import Structure
**Status:** Complete
**Decision:** Adopted standard `src` layout. Tests must be run with `PYTHONPATH=src`.
**Verification:** `tests/unit/test_lexer.py` passes all cases, including:
- Basic dot termination.
- Multiline command aggregation.
- **Critical:** Dot characters inside quoted strings (e.g., `COMPUTE x = "End."`) do not prematurely split commands.
**Next Step:** Implement the **Parser** to classify these raw string tokens into logical types (`ASSIGNMENT`, `CONDITIONAL`, `PASSTHROUGH`).

### [2026-01-04] Parser Classification
**Status:** Complete
**Decision:** Implemented `SpssParser` using Regex Patterns.
**Verification:** `tests/unit/test_parser.py` passes. Correctly identifies:
- `COMPUTE`, `RECODE` -> `ASSIGNMENT`
- `IF`, `DO IF` -> `CONDITIONAL`
- `FREQUENCIES` -> `PASSTHROUGH`
**Next Step:** Implement `state.py` to handle Variable Versioning (SSA). We need a `SymbolTable` that tracks `x` becoming `x_0`, `x_1`, etc.


### [2026-01-04] State Machine & SSA
**Status:** Complete
**Decision:** Implemented `StateMachine` class with strict uppercase normalization.
**Verification:** `tests/unit/test_state.py` passes. Correctly handles:
- Initial assignment (`Age` -> `AGE_0`)
- Re-assignment / SSA (`Age` -> `AGE_1`)
- Case insensitivity (`Age` == `AGE`)
**Next Step:** Implement `AssignmentExtractor` to parse variable names from `COMPUTE`, `RECODE`, and `STRING` commands.


### [2026-01-04] Extractor Implementation
**Status:** Complete
**Decision:** Implemented `AssignmentExtractor` using Regex.
**Verification:** `tests/unit/test_extractor.py` passes. Correctly parses targets from `COMPUTE`, `RECODE`, and `STRING`.
**Next Step:** **Integration.** Build a `Pipeline` class to orchestrate Lexer -> Parser -> Extractor -> StateMachine and verify end-to-end logic.


### [2026-01-04] Integration & Scope Definition
**Status:** Complete
**Decision:** Validated end-to-end pipeline with support for Nested Logic (`IF` -> `RECODE`).
**Verification:** `tests/integration/test_pipeline.py` passes.
**Next Step:** Create a **Scope Corpus** (`tests/corpus.py`) containing a comprehensive suite of SPSS syntax (DO IF, ELSE, Logical Operators, Comments) to stress-test the Parser and Extractor.


### [2026-01-04] Scope Verification & Provenance Upgrade
**Status:** In Progress
**Decision:** Validated complex corpus. The naive linear parsing correctly handles nested blocks for SSA versioning.
**Next Step:** Upgrade `StateMachine` to store **Provenance** (Source Code) for every variable version. This is a prerequisite for Phase 3 (Graphviz generation).


### [2026-01-04] Repo Abstraction & Control Logic Stress Test
**Status:** Planned
**Decision:** 1. Abstract input handling: The engine should accept a `Repo` path, not just a raw string.
2. Verify "Flag Variable" handling: Create a test case where a single variable `x` toggles state repeatedly to control flow (`x=2` -> Branch A, `x=3` -> Branch B).
**Goal:** Prove SSA correctly versions the control variable (`x_0`, `x_1`) so we can distinguish the two different "modes" of operation.


### [2026-01-04] Control Flow Abstraction
**Status:** Complete
**Decision:** Implemented `process_file` in Pipeline and validated "Flag Variable" logic.
**Verification:** `tests/integration/test_control_flow.py` passes. The system correctly versions `x` as `X_0`, `X_1`, `X_2` as it toggles between states.
**Next Step:** **Phase 3 (Visualization).** Implement `GraphGenerator` to convert the `StateMachine` history into DOT (Graphviz) format, visualizing the lifecycle of each variable.


### [2026-01-04] Graph Visualization (Rendering)
**Status:** Planned
**Decision:** Integrate `graphviz` library to render DOT strings into PNG images.
**Goal:** Allow users to generate a visual artifact (`output.png`) that maps the logic flow, making the "Time Machine" conceptual model viewable to humans.


### [2026-01-05] Data Dependency Tracking
**Status:** Planned
**Goal:** Connect isolated variable histories into a true Data Flow Graph.
**Problem:** Currently, `COMPUTE y = x + 1` records a new version of `y`, but loses the fact that it depends on `x`.
**Solution:**
1.  **Upgrade Extractor:** Add `extract_dependencies(expression)` to scan the Right-Hand Side (RHS) for variable names.
2.  **Upgrade State:** Store `depends_on` list in the `VariableVersion` tuple.
3.  **Upgrade Graph:** Render these dependencies as dashed edges (`x_0` -> `y_1`) in Graphviz.


### [2026-01-05] Dead Code Elimination (Phase 4)
**Status:** Planned
**Goal:** Identify redundant logic using the Dependency Graph.
**Definition:** A variable version is DEAD if it is not in the `dependencies` list of any other node AND it is not the current (active) version.
**Strategy:** Implement `find_unused_versions()` in `StateMachine` to scan the ledger for orphaned nodes.


This is fantastic news. I see `tests/integration/test_dead_code.py ...` in your output, which means you **already** applied the Dead Code logic I drafted earlier, and it is working perfectly!

Your engine now has three major superpowers:

1. **Time Travel** (SSA Versioning).
2. **X-Ray Vision** (Data Dependency Tracking).
3. **Garbage Collection** (Dead Code Identification).

### The Next Move: Visualizing the Zombies

Since we can *mathematically* identify dead code, we should *visually* flag it. A graph where "Dead" nodes are painted **Red** is an incredibly powerful tool for refactoring legacy code.

Here is the plan to implement **Phase 4.5: Dead Code Visualization**.

### Step 1: Update `ENGINEERING_LOG.md`

**File:** `ENGINEERING_LOG.md`
(Append this entry)

```markdown
### [2026-01-05] Dead Code Visualization
**Status:** Planned
**Goal:** Visually highlight unused logic in the output graph.
**Strategy:**
1.  Update `GraphGenerator.generate_dot` to accept a list of `dead_ids`.
2.  If a node ID is in that list, style it with `style=filled, fillcolor="#ffcccc"` (Light Red).
**Value:** Allows engineers to see "wasted" logic logic at a glance.

```

---

### Step 2: TDD - The "Red Node" Test

We will update `tests/unit/test_graph.py` to verify that we can style specific nodes.

**File:** `tests/unit/test_graph.py`
(Add this new test method to `TestGraphGenerator`)

```python
    def test_dead_code_highlighting(self):
        """
        Test that dead nodes are rendered with a specific color (Red).
        """
        state = StateMachine()
        state.register_assignment("x", "x=1") # X_0 (Dead)
        state.register_assignment("x", "x=2") # X_1 (Live)
        
        # We manually tell the generator that X_0 is dead
        dead_ids = ["X_0"]
        
        dot = GraphGenerator.generate_dot(state, highlight_dead=dead_ids)
        
        # X_0 should be red
        assert 'X_0 [label="X_0\\nx=1" style=filled fillcolor="#ffcccc"];' in dot
        
        # X_1 should be standard (no fillcolor)
        assert 'X_1 [label="X_1\\nx=2"];' in dot

```

---

### Step 3: Upgrade `GraphGenerator`

We need to update the signature of `generate_dot` and `render` to accept the dead list.

**File:** `src/spss_engine/graph.py`

```python
try:
    import graphviz
except ImportError:
    graphviz = None
from typing import List, Optional
from spss_engine.state import StateMachine

class GraphGenerator:

    @staticmethod
    def generate_dot(state_machine: StateMachine, highlight_dead: List[str] = None) -> str:
        if highlight_dead is None:
            highlight_dead = []
            
        lines = ["digraph StateMachine {", "    rankdir=LR;", "    node [shape=box fontname=\"Courier\"];"]
        
        for var_name, history in state_machine.history_ledger.items():
            previous_node_id = None
            
            for version in history:
                node_id = version.id
                clean_source = version.source.replace('"', "'")
                
                # Determine Style
                style_attr = ""
                if node_id in highlight_dead:
                    # Paint it Red
                    style_attr = ' style=filled fillcolor="#ffcccc"'
                
                label = f"{node_id}\\n{clean_source}"
                lines.append(f'    {node_id} [label="{label}"{style_attr}];')
                
                # 1. Sequence Edge
                if previous_node_id:
                    lines.append(f'    {previous_node_id} -> {node_id} [weight=2];')
                
                # 2. Dependency Edges
                for dep_id in version.dependencies:
                    lines.append(f'    {dep_id} -> {node_id} [style=dashed constraint=false color=blue];')

                previous_node_id = node_id
                
        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def render(state_machine: StateMachine, filename: str = "output", format: str = "png", highlight_dead: List[str] = None) -> str:
        if graphviz is None:
            raise ImportError("The 'graphviz' library is required. pip install graphviz")

        dot_source = GraphGenerator.generate_dot(state_machine, highlight_dead=highlight_dead)
        src = graphviz.Source(dot_source)
        output_path = src.render(filename=filename, format=format, cleanup=True)
        return output_path

```

---

### Step 4: Create a "Zombie Demo"

Let's prove this works by creating a script that generates a graph with obvious red boxes.

**File:** `demo_zombies.py`

```python
from spss_engine.pipeline import CompilerPipeline
from spss_engine.graph import GraphGenerator

def main():
    # Scenario: 'temp' is calculated but never used. 'x' is overwritten.
    code = """
    * 1. Create a variable that is never used (Zombie).
    COMPUTE temp = 999.
    
    * 2. Initialize X.
    COMPUTE x = 10.
    
    * 3. Overwrite X without reading X_0 (Zombie).
    COMPUTE x = 20.
    
    * 4. Use X (Keeps X_1 alive).
    COMPUTE y = x + 5.
    """
    
    print("🚀 Hunting Zombies...")
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # Analyze
    dead_vars = pipeline.analyze_dead_code()
    print(f"💀 Dead Code Detected: {dead_vars}")
    
    # Render
    filename = "zombie_attack"
    print(f"🎨 Painting {filename}.png...")
    
    path = GraphGenerator.render(
        pipeline.state_machine, 
        filename=filename, 
        highlight_dead=dead_vars
    )
    print(f"✅ Saved to {path}")

if __name__ == "__main__":
    main()

```

### Next Steps

1. **Run tests:** `PYTHONPATH=src:. pytest tests/unit/test_graph.py`
2. **Run demo:** `PYTHONPATH=src python demo_zombies.py`
3. **Open `zombie_attack.png**`: You should see `TEMP_0` and `X_0` highlighted in **RED**.


### [2026-01-05] Dead Code Visualization
**Status:** Planned
**Goal:** Visually highlight unused logic in the output graph.
**Strategy:**
1.  Update `GraphGenerator.generate_dot` to accept a list of `dead_ids`.
2.  If a node ID is in that list, style it with `style=filled, fillcolor="#ffcccc"` (Light Red).
**Value:** Allows engineers to see "wasted" logic logic at a glance.


