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
