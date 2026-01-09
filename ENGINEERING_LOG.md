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

### [2026-01-06] Phase 7: Repository Implementation
**Status:** In Progress
**Goal:** Enable batch processing of entire folders, not just single files.
**Strategy:**
1.  Create `Repository` class to recursively scan for `.spss` / `.sps` files.
2.  **Constraint:** Must explicitly filter out non-code files (e.g., `.txt`, `README.md`) to prevent parsing errors.
3.  **Refactor:** Update `statify.py` to use `Repository` instead of ad-hoc `os.walk` loops.

### [2026-01-06] Maintenance: Conductor / Mock LLM Fix
**Status:** Complete
**Issue:** `test_describer.py` failed because the `MockLLM` update for the Conductor phase dropped source code from its output, causing assertion errors in prompt verification tests.
**Fix:** Updated `MockLLM.describe_node` to echo the input source code, ensuring tests can verify data flow.


### [2026-01-06] Phase 7: Repository & End-to-End Verification
**Status:** Complete
**Features:**
1.  **Repository Class:** Implemented recursive file scanning with extension filtering (`.spss` only).
2.  **Statify CLI Refactor:** Updated to use `Repository` and support `--output` directory (keeping source clean).
3.  **End-to-End Test:** Created `tests/integration/test_end_to_end.py` which validates the full chain: `Source -> Compiler -> PSPP Runner -> Graph -> AI -> Markdown`.
**Outcome:** The system now generates a "Verified" badge in the spec if the PSPP probe succeeds.


### [2026-01-06] R Script Autopsy & The "Solid Graph" Mandate
**Status:** Critical Milestone
**Event:** Compared our Verified Spec against a generated R script for the same project.
**Findings:**
1.  **Verification Works:** Our `PsppRunner` correctly captured the legacy system's state.
2.  **Generative AI Failed:** The R script contained 4 critical logic errors (Time Travel, Invisible Join, Date Format, Precision Drift).
3.  **Root Cause:** The R script missed the `MATCH FILES` dependency, treating variables as "Magic Numbers" rather than derived data.
**Decision:** We must strictly model `MATCH FILES` and `SAVE OUTFILE` in the Graph. We cannot proceed to Phase 8 (Code Gen) until the Graph is fully connected, merging the current 12 disconnected chapters into a single coherent flow.


### [2026-01-06] Phase 7: Connectivity & The "File Bridge" Refactor
**Status:** Complete
**Goal:** Solve the "Fragmented Graph" problem where `MATCH FILES` commands broke the dependency chain, isolating variables into disconnected chapters.
**Architecture Changes:**
1.  **Parser Refactor:** Converted `SpssParser` from static methods to an instance-based class to support future stateful parsing features.
2.  **The File Bridge:**
    * **Parser:** Added support for `SAVE OUTFILE`, `SAVE TRANSLATE`, and `MATCH FILES`.
    * **Extractor:** Implemented regex to target filenames (artifacts) in command strings.
    * **State Machine:** Added a `file_registry`. When a script saves to `file.sav`, the state machine snapshots the current variable versions. When `MATCH FILES` loads `file.sav`, it creates dependency edges linking the new active variables back to those snapshots.
3.  **Pipeline Logic:** Enhanced `process()` to handle nested assignments within `CONDITIONAL` blocks (e.g., `IF (x) COMPUTE y=1`), ensuring hidden logic wasn't missed.

**Validation:**
* **Regression:** All 48 tests (Unit & Integration) passed after significant refactoring of the API signatures.
* **Real World:** Ran `statify` on `example_pspp_final.sps`. The generated Specification collapsed 12 disconnected chapters into a single "Super-Cluster" of logic, proving that the system correctly traced data flow through file I/O operations.
* **Verification:** The "Verified Execution" badge is active, confirming the logic matches the ground truth from PSPP.


### [2026-01-06] Phase 8 & 9: Code Generation & Equivalence Verification
**Status:** Complete
**Goal:** Prove that the Abstract Graph can be compiled into modern, correct R code.
**Achievements:**
1.  **The "Code Forge":** Created `src/code_forge/` containing `RGenerator` and `RRunner`.
2.  **Smart Transpilation:** * Converts `COMPUTE` -> `mutate()`.
    * Converts `IF` -> `if_else()`.
    * Enforces `snake_case` variable naming for R style compliance.
    * Generates `DESCRIPTION` file for R package compatibility.
3.  **The "Equivalence Engine":** * Implemented `statify.py --code` to run an immediate "Back-to-Back" test.
    * Executes Legacy Code (PSPP) and New Code (R) in parallel.
    * Compares output variables with type-aware logic (Float vs String handling).
**Result:** Achieved `✅ PROVEN EQUIVALENCE` on the Payroll Demo.


### [2026-01-06] Phase 10: The Rosetta Stone & Robust Translation
**Status:** Complete
**Goal:** Handle complex legacy syntax (Date Math, Joins, Modulo) without brittle regex hacking.
**Achievements:**
1.  **The Rosetta Stone:** Created `src/code_forge/rosetta.py` as a centralized dictionary for SPSS -> R translations.
2.  **Smart Parsing:** Implemented `_split_args` to handle nested parentheses in function calls (e.g., `DATE.MDY(TRUNC(MOD(...)))`).
3.  **Join Logic:** `RGenerator` now detects `MATCH FILES` and transpiles them into `dplyr::left_join`.
4.  **TDD Discipline:** Wrote unit tests (`test_rosetta.py`, `test_generator_joins.py`) *before* implementation to ensure robustness.
**Result:**  the unit test suite is 100% Green (63 tests).


### [2026-01-06] Phase 11: Architecture Hardening (AI Abstraction)
**Status:** In Progress
**Goal:** Prevent AI timeouts from corrupting generated code and centralize LLM configuration.
**Issues:**
* `OllamaClient` timeout (30s) is too short for code refactoring.
* Exception swallowing in `OllamaClient` caused `[AI Error]` to be written as source code.
**Actions:**
1.  **Refactor:** Extract `OllamaClient` to `src/common/llm.py`.
2.  **Refactor:** Extract prompts to `src/common/prompts.py`.
3.  **Resilience:** Increase default timeout to 120s.
4.  **Safety:** Ensure `CodeRefiner` falls back to "Rough Draft" code on AI failure.

### [2026-01-06] Phase 11: Architecture Hardening & AI Refinement
**Status:** Complete
**Goal:** Integrate GenAI to clean up complex syntax without breaking the build.
**Achievements:**
1.  **Refactoring:** Centralized AI logic in `src/common` to eliminate circular dependencies and dead code.
2.  **Safety:** Implemented a "Fall Back to Rough Draft" strategy. If the AI times out or hallucinations, the system uses the deterministic (but ugly) transpiled code.
3.  **Integration Testing:** Added `test_refinement_flow.py` to verify the "Handshake" between the Generator and the AI service.
4.  **Verification:** `demo_refine.py` proved that `qwen2.5-coder` can successfully refactor multi-line SPSS legacy date logic into clean `lubridate::make_date` calls.
**Result:** System is now resilient to AI failures and capable of producing human-grade R code.


## 2026-01-07: The Rosetta & Conductor Update

### 🚀 Critical Fixes
1.  **Fixed `RosettaStone` Recursion:**
    * Problem: Simple regex replacements failed on nested functions like `DATE.MDY(TRUNC(x), ...)` and broke `AGE >= 18` into `AGE >== 18`.
    * Solution: Implemented a recursive `_split_args` parser and Regex Lookbehind assertions. The translator now correctly handles deeply nested legacy syntax.

2.  **Fixed `RRunner` Error Reporting:**
    * Problem: The runner was swallowing R syntax errors, making debugging impossible.
    * Solution: Updated the R wrapper to capture `stderr` and bubble "CRITICAL R ERROR" up to the Python exception handler.

3.  **Sanitized Graph Visualization:**
    * Problem: `MATCH FILES` commands containing `/` or quotes crashed Graphviz.
    * Solution: Implemented robust label sanitization in `GraphGenerator`.

### 🧠 Architectural Discovery: Scope Leakage
* **Observation:** The generator produced R code that tried to calculate `min_age_n` using a raw variable `value`.
* **Root Cause:** The legacy script (`example_pspp_final.sps`) reused the variable name `value` in a localized ETL step (loading `control_vars.csv`) before the main pipeline started. Our State Machine treated this as a global dependency.
* **Validation:** Created `tests/integration/test_spec_structure.py`. This test successfully proved that the `Conductor` can distinguish between the **Control Vars Cluster** and the **Main Calculation Cluster**.
* **Next Step:** Update `RGenerator` to respect these clusters, generating separate R functions (or pipelines) for each cluster to prevent variable leakage.

### ✅ Test Coverage
* `tests/integration/test_spec_structure.py`: PASSED (Proves we can segregate logic).
* `tests/unit/test_rosetta.py`: PASSED (Proves syntax translation is robust).
* `tests/unit/test_writer.py`: PASSED (Proves conditional logic generation).


## 2026-01-07: The Stabilization & Refactor

### 🔧 Architectural Pivot: The "Zoom In / Zoom Out" Strategy
* **Challenge:** The "Complexity Level 3" test revealed a fundamental flaw. The engine either treated the entire script as one giant graph (Spaghetti) or broke connections entirely (Amnesia).
* **Solution:** We separated **Variable Logic** from **File I/O Logic**.
    * `StateMachine.reset_scope()`: Clears the variable ledger when loading new data, ensuring perfectly isolated documentation for each step.
    * `ClusterMetadata`: Records inputs and outputs persistantly.
* **Result:** We can now accurately describe "Step B computes Average Sales" (Micro) AND "Step B depends on Step A's output" (Macro).

### ♻️ The Great Refactor
* **Pipeline:** Refactored `CompilerPipeline` to use a `dispatch_table`. This allows us to support complex commands like `AGGREGATE` and `MATCH FILES` cleanly.
* **Compatibility Rescue:** The refactor initially broke 27 legacy tests due to API changes (`source_code` vs `source`). We restored the original API signature while keeping the new internal logic, bringing the test suite back to 100% Green.

### ✅ Verification
* `tests/integration/test_cluster_io.py`: **PASSED** (Proves Isolation + Linkage).
* `tests/integration/test_spec_complexity_levels.py`: **PASSED** (Proves we handle complex Aggregation flows).
* `tests/unit/test_state.py`: **PASSED** (Proves Core Logic is stable).


## 2026-01-07: Core Data Structures Verification
* **Component:** `VariableVersion`, `ClusterMetadata`, `ParsedCommand`
* **Action:** Created `tests/unit/test_data_structures.py` to verify default factories, ID generation logic, and Enum integration.
* **Outcome:** Confirmed that data carriers initialize safely without mutable default argument bugs.


## 2026-01-07: Pipeline File & Utility Verification
* **Component:** `CompilerPipeline`
* **Action:** Created `tests/unit/test_compiler_pipeline.py` to target file I/O safety and Dead Code filtering logic.
* **Outcome:** Validated `FileNotFoundError` handling and confirmed that system-internal nodes (Joins) are correctly excluded from Dead Code reports.


## 2026-01-07: External Runner Isolation
* **Component:** `PsppRunner`, `RRunner`
* **Action:** Created `tests/unit/test_runners.py` using `subprocess` mocks.
* **Outcome:** Verified that runners correctly handle non-zero exit codes (raising `RuntimeError`) and construct the correct CLI arguments for `pspp` and `Rscript`.


## 2026-01-07: Code Forge Tooling Tests
* **Component:** `CodeOptimizer`, `CodeRefiner`
* **Action:** Created `tests/unit/test_code_forge_tools.py`.
* **Outcome:** Verified dependency checking logic (e.g., detecting if R is installed) and the LLM interaction loop for code refinement.


## 2026-01-07: The "Audit & Harden" Phase (100% Coverage)

### 🎯 Objective
Eliminate "Hidden Risk" by auditing the codebase against the test suite and filling all coverage gaps.

### 🛠️ Key Actions
1.  **Functionality Audit:** Deployed `map_codebase.py` to identify 11 untested components.
2.  **Orchestrator Verification:** Created `tests/unit/test_orchestrator.py`.
    * *Bug Found:* `SpecGenerator` output was missing source code, causing verification failures.
    * *Fix:* Updated `SpecGenerator` to include source blocks in Markdown.
3.  **Runner Verification:** Created `tests/unit/test_runners.py`.
    * *Bug Found:* `RRunner` was dropping script arguments.
    * *Bug Found:* `PsppRunner` was failing silently on syntax errors.
    * *Fix:* Aligned runner logic with the actual `run_wrapper.R` architecture and added strict error checking.
4.  **Core Hardening:** Created `tests/unit/test_compiler_pipeline.py` and `tests/unit/test_data_structures.py`.
    * *Bug Found:* Dead Code Analysis incorrectly protected single-assignment variables.
    * *Fix:* Refined the "Survivor Rule" in `state.py`.

### ✅ Result
* **Code Map:** 100% Component Coverage (23/23).
* **Stability:** The system is now robust against the exact failures that were plaguing the End-to-End test (Runner crashes, Orchestrator misconfiguration).


## 2026-01-07: Code Forge Tools Verification
* **Component:** `CodeOptimizer`, `CodeRefiner`
* **Action:** Created `tests/unit/test_code_forge_tools.py` and patched implementation signature mismatches.
* **Fixes:**
    * Updated `CodeOptimizer` to accept `project_dir` (Dependency Injection).
    * Updated `CodeRefiner` to handle `MagicMock` serialization issues by patching the internal `OllamaClient`.
    * Corrected `CodeRefiner.refine` signature assumptions.
* **Outcome:** The Code Forge toolchain is now fully unit-tested and compatible with the new architecture.


## 2026-01-07: The "Statify" Stabilization (v1.0 Release Candidate)

### 🎯 Objective
Achieve 100% test pass rate across Unit, Integration, and End-to-End suites by synchronizing the Legacy CLI with the New Architecture.

### 🛠️ Key Actions
1.  **Graph Generator API Fix:**
    * *Issue:* `SpecOrchestrator` and `statify.py` were calling `GraphGenerator.render(filename=...)`.
    * *Fix:* Enforced `render(output_path)` signature in `src/spec_writer/graph.py` and updated all callers.
    * *Verification:* Created `tests/unit/test_graph_render.py` to lock this contract.
2.  **CLI Synchronization:**
    * *Issue:* `statify.py` was manually wiring legacy components, bypassing the `SpecOrchestrator`.
    * *Fix:* Updated `statify.py` to use the new `GraphGenerator` class instance and positional arguments.
3.  **Handoff Verification:**
    * Created targeted integration tests (`test_graph_handoff.py`, `test_markdown_handoff.py`) to isolate subsystem failures before running E2E.

### ✅ Result
* **Test Suite:** 103 Tests Passed (0 Failures).
* **Coverage:** 100% Component Functionality.
* **Status:** The system is now robust, verified, and ready for deployment.


## [2026-01-08] Recovery: The Data Bridge Fix

**Branch:** `feature/fix-r-generation-and-mocking`
**Status:** Complete

### Context
Recovered from a git branch scramble. The goal was to finalize the R Transpilation pipeline, ensuring that legacy SPSS `RECODE` logic is correctly ported to R and that the verification runner (which proves the R code works) is smart enough to mock missing input data.

### Technical Implementation

#### 1. The Object/String Duality Fix
* **Component:** `src/spss_engine/state.py`
* **Issue:** The generator logic assumed dependencies were stored as strings (IDs), but they were `VariableVersion` objects. This caused `.rsplit` errors.
* **Fix:** Added `__str__` dunder method to `VariableVersion` returning `self.id`. Updated `RGenerator._transpile_node` to explicitly access `.id` when normalizing RHS expressions.

#### 2. R Logic Generation (RECODE)
* **Component:** `src/code_forge/generator.py`
* **Logic:** Implemented a regex parser for `RECODE var (old=new)`.
* **Transformation:** * SPSS: `RECODE x (1=10) (ELSE=99).`
    * R: `mutate(x = case_when(x == 1 ~ 10, TRUE ~ 99))`

#### 3. Auto-Discovery for Mock Data
* **Component:** `src/code_forge/runner.py`
* **Improvement:** The runner was dumb; it didn't know what variables the script needed.
* **Change:** Injected `StateMachine` into `RRunner`. Added `_discover_inputs()` method which calculates `Required Vars - Defined Vars` to identify inputs (e.g., `weight`, `height`). These are now initialized as `1` in the R wrapper to prevent execution crashes.

### Outcome
All unit tests passed. End-to-end verification of the BMI pipeline is now green. The system can successfully intake SPSS logic, convert it to R, and verify it runs without crashing on missing variables.