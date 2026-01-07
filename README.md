# State Machine: Legacy Code Modernization Engine

## 1. Philosophy & Motivation

**"We are not building a translator; we are building a de-compiler for logic."**

This project represents a fundamental pivot from standard AI-assisted coding tools. The prevailing industry approach is to feed legacy code (like SPSS) into a Large Language Model (LLM) and ask it to "rewrite this in Python." This approach is fundamentally flawed for critical business logic because:

1. **Hallucination Risk:** LLMs are constructive engines, not analytic ones. They prioritize plausibility over mathematical accuracy.
2. **Context Window Limits:** A 7B (or even 70B) parameter model cannot reliably track the state of a variable across 2,000 lines of spaghetti code without losing the thread.
3. **The "Black Box" Problem:** We reject the idea of a tool that asks the user to trust a stochastic process. We demand a tool that prioritizes **User Utility** and **Deterministic Auditability**.

### The "State Machine" Approach

Instead of asking an AI to *understand* the code, we build a deterministic Python engine to *model* the code.

* We treat the legacy script not as text, but as a **Control Flow Graph (CFG)**.
* We use **Static Single Assignment (SSA)** to version variables over time (turning `x` into `x_0`, `x_1`, `x_2`), effectively creating a "Time Machine" that allows us to audit the state of data at any specific line.
* **The Role of AI:** The AI (a local 7B model) is demoted from "Architect" to "Decorator." It is used only for narrow, strictly scoped tasks—such as renaming `var_05` to `Adult_Flag` based on a mathematically proven logic block—where its ability to hallucinate is constrained by the rigid structure of our State Machine.

This architecture ensures that the final output is not just a "guess" at what the code does, but a mathematically verified specification of the data flow.

---

## 2. Architecture

The engine functions like a modern optimizing compiler (e.g., LLVM), but running in reverse.

### Phase 1: The Crawler (Lexer)

A robust, regex-based Lexer capable of parsing the inconsistent syntax of legacy languages (specifically SPSS/PSPP).

* **Goal:** Normalize the input stream, handling multi-line commands and dot-termination logic reliably.
* **Status:** Implemented (`src/spss_engine/lexer.py`).

### Phase 2: The State Machine (The Engine)

This is the core of the project. It walks through the parsed commands and maintains a **Symbol Table** of the data environment.

* **Variable Versioning (SSA):** If the code assigns `x = 1` and later `x = 2`, the engine tracks these as distinct entities (`x_1`, `x_2`). This resolves the "mutability of time" problem inherent in procedural coding.
* **Phi Functions (Φ):** When branching logic (IF/ELSE) merges back together, the engine generates a Phi function (`x_3 = Φ(x_1, x_2)`) to mathematically represent uncertainty/conditional states.

### Phase 3: The Intermediate Representation (IR)

The engine does not output English; it outputs a **Graph**.

* We use the **DOT language** (Graphviz) to visualize the logic flow.
* This allows us to perform **Dead Code Elimination**: if a branch leads to a state that is never used, we prune it *before* the human (or AI) ever sees it.

### Phase 4: The "Human Spec" Generator

Once the logic is distilled to its essence (The "True Path"), we pass the simplified State Objects to a 7B Parameter LLM.

* **Prompt:** "Variable `v_1` is set to 5 when `Age > 18`. Rename `v_1` to a human-readable label."
* **Output:** A clean, human-readable specification derived from ground-truth logic.

---

## 3. Project Structure

```text
state_machine/
├── src/
│   └── spss_engine/
│       ├── lexer.py         # Breaks raw text into discrete commands
│       ├── parser.py        # Regex dictionary mapping commands to Logic Actions
│       ├── state.py         # The SSA Engine and Symbol Table logic
│       └── graph.py         # Generates DOT/Graphviz visualizations
├── tests/
│   ├── unit/                # Unit tests for individual components
│   └── integration/         # End-to-end tests on real SPSS scripts
├── requirements.txt         # Dependencies (pytest, graphviz, etc.)
└── README.md                # You are here

```

---

## 4. Goals

1. **Strict Auditability:** Every sentence in the final spec must be traceable to a specific, versioned variable transformation in the original code.
2. **Local Execution:** The system runs on a local environment (Linux/PSPP compatibility). No data is sent to external APIs, preserving security and privacy (The "Solipsistic" requirement).
3. **Complexity Reduction:** Iteratively simplify code by identifying and removing logic that does not affect the final state ("Dead Code").

---

## 5. Getting Started

### Prerequisites

* Python 3.8+
* `pytest` for testing
* (Optional) `pspp` installed on Linux for verifying legacy script behavior.

### Installation

1. **Clone the repository:**
```bash
git clone <repo_url>
cd state_machine

```


2. **Set up Virtual Environment:**
```bash
python3 -m venv venv
source venv/bin/activate

```


3. **Install Dependencies:**
```bash
pip install -r requirements.txt

```



### Running Tests

We enforce a strict TDD (Test Driven Development) workflow. New features must pass existing tests.

```bash
# Run all tests with coverage
PYTHONPATH=src pytest

```

---

## 6. Next Steps & Roadmap

* [x] **Step 0:** Define Project Structure & Philosophy.
* [x] **Step 1:** Implement robust Lexer (`lexer.py`).
* [ ] **Step 2:** Build the Regex Dictionary for SPSS Commands (The "Parser").
* [ ] **Step 3:** Implement the State Object class (`state.py`) to handle SSA Versioning.
* [ ] **Step 4:** Create the DOT Generator to visualize the Control Flow Graph.
* [ ] **Step 5:** Connect the 7B Model (Local LLM) to describe the State Transitions.

---

## 🚀 Current Status: The "Parser Wall" is Breached

As of **Jan 2026**, the core SSA Engine is operational and fully unit-tested. We have successfully moved beyond simple text processing to semantic state tracking.

**Capabilities:**
* **Robust Lexing:** Can handle multi-line commands, messy whitespace, and edge cases like dots inside quoted strings (`"End."`).
* **Semantic Parsing:** Classifies commands into `ASSIGNMENT`, `CONDITIONAL`, and `PASSTHROUGH` logic blocks.
* **Static Single Assignment (SSA):** The engine mathematically versions variables over time (e.g., `Age` becomes `AGE_0`, then `AGE_1`), creating a deterministic timeline of data transformation.
* **Logic Provenance:** Every variable version is linked directly to the source code that created it, ensuring full auditability.
* **Nested Logic Support:** Successfully parses assignments inside `IF` and `DO IF` blocks (e.g., `IF (x) RECODE y`).

**Verified Against Corpus:**
The system passes a comprehensive integration suite (`tests/corpus.py`) covering:
* Variable Initialization & Arithmetic
* `IF` / `ELSE IF` / `DO IF` Control Structures
* `RECODE` (both In-Place and `INTO` variations)
* Complex logical operators and commenting styles

### 🏗️ Architecture Component Status

| Component | Status | Responsibility |
| :--- | :--- | :--- |
| **Lexer** | ✅ Done | Tokenizes raw text; handles SPSS "dot termination" rules. |
| **Parser** | ✅ Done | Classifies tokens into logical types (`ASSIGNMENT`, `CONDITIONAL`). |
| **Extractor** | ✅ Done | Isolates target variables from complex commands (`COMPUTE`, `RECODE`). |
| **State Machine** | ✅ Done | Manages the Symbol Table and SSA Versioning (`AGE_0` -> `AGE_1`). |
| **Pipeline** | ✅ Done | Orchestrates the flow: `Raw Text -> Graph State`. |
| **Graph Viz** | 🚧 Next | Convert the State Machine history into DOT/Graphviz diagrams. |

### 🛠️ Usage Example

The pipeline can now be invoked programmatically to analyze legacy scripts:

```python
from spss_engine.pipeline import CompilerPipeline

code = """
COMPUTE Age = 25.
IF (Age < 18) RECODE Status ('Child'=1).
"""

pipeline = CompilerPipeline()
pipeline.process(code)

# Query the deterministic state
current_version = pipeline.get_variable_version("Status") 
# Returns: "STATUS_1"

# Audit the history
history = pipeline.get_variable_history("Status")
# Returns: [
#    VariableVersion(id='STATUS_0', source="STRING Status..."),
#    VariableVersion(id='STATUS_1', source="RECODE Status...")
# ]

```

---

### 🔮 Immediate Roadmap

1. **Graph Generation (Phase 3):** Visualize the `StateHistory` as a Directed Acyclic Graph (DAG) using Graphviz.
2. **Dead Code Elimination:** Use the graph to identify variable versions that are created but never read.
3. **LLM Integration (Phase 4):** Feed the cleaned graph nodes to a 7B model for human-readable summarization.

```

```
This is a perfect stopping point. We have established a complete, verified pipeline from "Raw Code" to "Verified English Spec."

Here are the updated files. I have integrated all our recent wins (Ollama, Conductor, PSPP Verification, Statify CLI) into the documentation so we can resume exactly where we left off.

### 1. `ENGINEERING_LOG.md` (Updated)

I have added the completion logs for Phase 5 and 6, plus the new Verification layer.

```markdown
# Engineering Log

## Current Architecture
**Pattern:** State Machine / Decompiler / Semantic Analysis
**Goal:** Parse SPSS code into a Control Flow Graph (CFG), verify logic with PSPP, and generate human-readable specs using LLM clustering.

## Decision Journal

### [2026-01-04] Pivot to State Machine Architecture
**Reason:** The previous "Evolution Engine" (LLM-based translation) was non-deterministic.
**Action:** Created `src/spss_engine` as the new core using SSA (Static Single Assignment).

### [2026-01-04] Core Engine Implementation (Phases 1-3)
**Status:** Complete
**Components:**
1. **Lexer:** Handles "dot termination" and strings (`lexer.py`).
2. **Parser/Extractor:** Classifies commands (`ASSIGNMENT`, `CONDITIONAL`) and isolates variables.
3. **State Machine:** Implements SSA versioning (`x` -> `x_0`, `x_1`) and provenence tracking.
**Verification:** All unit/integration tests passing.

### [2026-01-04] Visualization & Dead Code (Phase 4)
**Status:** Complete
**Feature:** Graphviz generation (`graph.py`) with Dead Code highlighting.
**Outcome:** We can mathematically identify and visually flag logic that is never used ("Zombies").

### [2026-01-05] Phase 5: LLM Integration (The Scribe)
**Status:** Complete
**Decision:** Integrated `OllamaClient` to connect to local models (`mistral:instruct` / `llama3`).
**Architecture:** `SpecGenerator` iterates through **Live** nodes (ignoring Dead Code) and prompts the LLM for one-sentence descriptions.
**Verification:** `demo_ollama.py` proved we can translate `Net = Gross - Tax` into English prose.

### [2026-01-05] Phase 6: The Conductor (Clustering)
**Status:** Complete
**Problem:** Output was a flat, unreadable list of 100+ variables.
**Solution:** Implemented `Conductor` class (`conductor.py`) using **Weakly Connected Components (BFS)** to identify "islands" of logic.
**Feature:**
1. **Clustering:** Groups related variables (e.g., "Demographics" vs "Payroll").
2. **Topological Sort:** Ensures dependencies (`Gross`) are explained before dependents (`Net`).
3. **Auto-Titling:** LLM generates a Chapter Title based on the variables in the cluster.
**Verification:** `statify.py` successfully split `payroll.spss` into two distinct chapters.

### [2026-01-05] Ground Truth Verification (The Probe)
**Status:** Complete
**Goal:** Prove the engine's "understanding" matches reality.
**Implementation:** `PsppRunner` class (`runner.py`) injects a `SAVE TRANSLATE` command into scripts to dump the final state to CSV.
**Outcome:** We can now run any legacy script via `pspp` and assert that `Net_Pay` actually equals `40,000`, creating a feedback loop between our Graph and the runtime reality.
**Constraint:** Must use `/FIELDNAMES` in PSPP to ensure CSV headers are generated.

### [Next Session] Phase 7: Scaling & Repository Management
**Status:** Planned
**Goal:** Move from single-file analysis (`statify.py`) to whole-repo analysis.
**Plan:**
1.  Integrate the `Repository` class (`repository.py`) to manage file loading.
2.  Implement "Cross-File Dependencies" (e.g., `INSERT FILE` or `MATCH FILES`).
3.  Add "Verified" Badges to the generated spec if `PsppRunner` confirms the logic.

```

---

### 2. `README.md` (Updated)

I have updated the status, added the new CLI tool, and refreshed the architecture table.

```markdown
# State Machine: Legacy Code Modernization Engine

## 1. Philosophy

**"We are not building a translator; we are building a de-compiler for logic."**

This project rejects the "Black Box" approach of simply asking an LLM to rewrite code. Instead, we use a deterministic Python engine to:
1.  **Model** the code as a Control Flow Graph (CFG).
2.  **Verify** the logic using SSA (Static Single Assignment) and PSPP runtime probes.
3.  **Explain** the logic using an LLM as a "Decorator," not an Architect.

This ensures strict auditability: every sentence in the final English specification is backed by a specific, traceable node in the Logic Graph.

---

## 2. Capabilities

As of **Jan 2026**, the system is fully operational as a **Semantic De-compiler**.

### Core Features
* **Time Travel (SSA):** Distinguishes between `x` at line 10 (`x_0`) and `x` at line 50 (`x_1`).
* **Zombie Detection:** Mathematically identifies "Dead Code" (logic that is calculated but never used) and visualizes it in Red.
* **The Conductor:** Automatically clusters variables into logical "Chapters" (e.g., separating "Payroll Logic" from "Demographics Logic") using Graph Topology.
* **Ground Truth Verification:** Runs the legacy code using `pspp` to confirm that the Engine's calculations match reality.

---

## 3. Architecture

| Phase | Component | Status | Responsibility |
| :--- | :--- | :--- | :--- |
| **1** | `Lexer` | ✅ Done | Normalizes raw text and handles "dot termination". |
| **2** | `Parser` | ✅ Done | Classifies commands (`ASSIGNMENT`, `CONDITIONAL`). |
| **3** | `State Machine` | ✅ Done | SSA Engine. Tracks provenance and data dependencies. |
| **4** | `GraphGenerator` | ✅ Done | Renders `.png` diagrams. Highlights Dead Code. |
| **5** | `SpecGenerator` | ✅ Done | Connects to Local LLM (Ollama) to describe logic. |
| **6** | `Conductor` | ✅ Done | Clusters logic into topological "Chapters". |
| **V** | `PsppRunner` | ✅ Done | Verifies logic against the actual PSPP runtime. |

---

## 4. Usage: "Statify"

The primary entry point is the `statify` CLI tool. It transforms a legacy file (or folder) into a verified documentation package.

### Command
```bash
# Analyze a single file
PYTHONPATH=src python statify.py legacy/payroll.spss --model mistral:instruct

# Analyze an entire folder
PYTHONPATH=src python statify.py legacy_project_v1/

```

### Output Artifacts

For every input file (e.g., `payroll.spss`), the system generates:

1. **`payroll_flow.png`**: A visual map of the logic. "Dead" variables are painted Red.
2. **`payroll_spec.md`**: A structured Business Specification, organized into Chapters, with titles generated by the AI.

---

## 5. Development Setup

### Prerequisites

* Python 3.12+
* `pspp` (for Ground Truth verification)
* `ollama` (running locally for AI description)

### Installation

```bash
git clone <repo_url>
cd state_machine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### Running Tests

We use `pytest` for all verification.

```bash
# Run Unit, Integration, and Verification tests
PYTHONPATH=src:. pytest

```

---

## 6. Next Steps (Phase 7)

We are currently moving from **Single File Analysis** to **Repository Analysis**.

* [ ] **Repository Class:** Manage state across multiple files.
* [ ] **Cross-File Dependencies:** Handle `INSERT FILE` and `MATCH FILES`.
* [ ] **Verified Badging:** Automatically mark specs as "Verified" if `PsppRunner` confirms the output values.

```

### How to Resume
When we pick this up again, simply:
1.  **Verify Environment:** `source venv/bin/activate`
2.  **Verify Ollama:** `ollama serve`
3.  **Run Tests:** `PYTHONPATH=src:. pytest`
4.  **Start Phase 7:** We will begin implementing `src/spss_engine/repository.py` to handle the batch processing logic we started discussing.

```
---

## Appendix A: The Architecture of Legacy Logic

### Why SPSS is the Perfect Candidate for Static Analysis

Users often ask why we treat SPSS scripts as rigorous mathematical graphs rather than simply "translating" them to Python. The answer lies in the structural differences between SPSS and modern multi-paradigm languages (Python, R). While SPSS is syntactically dated, its limitations are actually **architectural features** that make deterministic modeling possible.

#### 1. The Advantage of "Value Semantics"

In languages like Python or R, variable assignment often implies reference (pointers). Writing `b = a` creates an alias; modifying `b` might secretly modify `a`. To model this, an engine must track the Heap and the Stack, leading to complex "Alias Analysis."

* **The SPSS Reality:** SPSS uses strict **Value Semantics**. `COMPUTE Y = X` creates a distinct copy. There are no pointers, no objects, and no "Action at a Distance."
* **Our Advantage:** This means our Dependency Graph is clean. An edge from `X` to `Y` is always a direct causal link, never a shared memory reference.

#### 2. The "Implicit Loop" Architecture

SPSS scripts do not run top-to-bottom like a Python script. Instead, the entire script functions as the **inner body of a loop** that iterates over a dataset.

* **The Model:** We do not need to model the iteration itself. Our State Machine models the **Abstract Transformation Rules** applied to a single generic row.
* **The Consequence:** This allows us to flatten the logic into a linear sequence of transformations without needing to simulate the state of 1,000,000 rows of data.

#### 3. The "Geological" Nature of Legacy Code

Modern code is refactored; legacy SPSS code is **accreted**.

* **The Pattern:** Logic is rarely deleted. Instead, new logic is appended to the bottom of the file to "fix" or "overwrite" previous calculations. A script might calculate `Net_Pay` on line 50, only to recalculate it on line 500 because of a 2012 policy change.
* **The Solution:** This "Append-Only" culture creates the specific problem our engine is designed to solve: **Dead Code**. By using Static Single Assignment (SSA), we can mathematically prove that the calculation on line 50 is never read by the final output, allowing us to treat it as a "Zombie" and prune it from the final specification.

#### 4. The Graph Topology (DAG vs. Tree)

While flowcharts are often visualized as Trees (splitting infinitely), business logic is almost always a **Directed Acyclic Graph (DAG)**.

* **Merge Points:** Branches (IF/ELSE) usually split to handle edge cases but strictly merge back together to form a final dataset.
* **Phi Functions:** Our engine handles these merge points using SSA Phi functions (), ensuring that the system can deterministically track a variable's state even when its history branches.

### Summary

We are not building a translator; we are building a **Digital Archaeology Tool**. We rely on the simplicity and procedural nature of SPSS to brush away layers of dead logic, revealing the clean, deterministic skeleton of the business rules underneath.

---

# 🗺️ State Machine Migration Engine

> **Status:** Beta (Core Logic Verified)
> **Latest Victory:** Automated translation of nested date logic (`DATE.MDY`) and discovery of implicit data streams (`MATCH FILES`).

## 🏗️ Architecture
We moved away from "Regex-based Transpilation" to a **State-Machine-Driven Architecture**. The system builds a dependency graph of the legacy logic before writing a single line of new code.

### 1. The Core Engine (`src/spss_engine`)
* **Lazy Parser:** Identifies command types (`COMPUTE`, `MATCH FILES`, `IF`) without executing them.
* **State Machine:** The Single Source of Truth. It registers every variable version (`var_0`, `var_1`) and tracks dependencies.
* **Conductor:** Analyzes the graph to identify "Logic Clusters" (separating ETL steps from Main Calculation steps).

### 2. The Builder (`src/code_forge`)
* **Generator:** Walks the State Machine to write modern R code (`dplyr`).
* **Rosetta Stone:** A recursive translation layer that handles complex nested functions (e.g., `DATE.MDY(TRUNC(MOD(...)))` $\to$ `make_date(...)`).
* **Runner:** Executes the generated R code to prove **Mathematical Equivalence** against the legacy system.

### 3. The Scribe (`src/spec_writer`)
* **Spec Generator:** Uses the `Conductor`'s clusters to write human-readable documentation, organizing spaghetti code into logical "Chapters".
* **Architect:** An AI agent that reviews the generated Code and Spec for logic gaps and library misuse.

---