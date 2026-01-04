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