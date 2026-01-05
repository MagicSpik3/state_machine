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
3.