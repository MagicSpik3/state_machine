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