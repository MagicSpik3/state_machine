🕵️  Scanning tests in `tests`...

# 🗺️ Codebase Functionality Map
**Root:** `/home/jonny/git/state_machine/src`

## 📦 Package: `src/common`

### 📄 `llm.py`
- ✅ 🏛️ **OllamaClient**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_llm.py::TestOllamaClient`
    - *Methods:* generate

---
## 📦 Package: `src/spec_writer`

### 📄 `conductor.py`
- ✅ 🏛️ **Conductor**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_conductor.py::TestConductor`
    - *Methods:* identify_clusters, _topological_sort, get_cluster_metadata

### 📄 `describer.py`
- ✅ 🏛️ **SpecGenerator**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_describer.py::TestSpecGenerator`
    - *Methods:* generate_report, _find_node_by_id, _get_node_source, _describe_node

### 📄 `graph.py`
- ✅ 🏛️ **GraphGenerator**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_graph.py::TestGraphGenerator`
    - *Methods:* _sanitize_label, generate_dot, render

### 📄 `orchestrator.py`
- ✅ 🏛️ **SpecOrchestrator**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_orchestrator.py::TestSpecOrchestrator`
    - *Methods:* ingest, generate_comprehensive_spec

### 📄 `review.py`
- ✅ 🏛️ **ProjectArchitect**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_architect.py::TestProjectArchitect`
    - *Methods:* review, _summarize_spec

---
## 📦 Package: `src/code_forge`

### 📄 `generator.py`
- ✅ 🏛️ **RGenerator**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_writer.py::TestRGenerator`
    - *Methods:* generate_description, _get_join_blocks, generate_script, _transpile_node, _topological_sort, _analyze_contract, _transpile_node, _topological_sort, _analyze_contract

### 📄 `optimizer.py`
- ✅ 🏛️ **CodeOptimizer**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_code_forge_tools.py::TestCodeForgeTools`
    - *Methods:* _ensure_paths, check_dependencies, run_linter, optimize_file

### 📄 `refiner.py`
- ✅ 🏛️ **CodeRefiner**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_code_forge_tools.py::TestCodeForgeTools`
    - *Methods:* refine

### 📄 `rosetta.py`
- ✅ 🏛️ **RosettaStone**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_rosetta.py::TestRosettaStone`
    - *Methods:* _split_args, translate_expression

### 📄 `runner.py`
- ✅ 🏛️ **RRunner**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_runners.py::TestRunners`
    - *Methods:* run_and_capture, _read_first_row

---
## 📦 Package: `src/spss_engine`

### 📄 `extractor.py`
- ✅ 🏛️ **AssignmentExtractor**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_extractor.py::TestAssignmentExtractor`
    - *Methods:* _normalize, extract_target, extract_dependencies, extract_file_target, extract_file_target

### 📄 `lexer.py`
- ✅ 🏛️ **SpssLexer**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_lexer.py::TestSpssLexer`
    - *Methods:* get_commands, normalize_command

### 📄 `parser.py`
- ✅ 🏛️ **TokenType**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_data_structures.py::TestDataStructures`
- ✅ 🏛️ **ParsedCommand**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_data_structures.py::TestDataStructures`
- ✅ 🏛️ **SpssParser**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_parser.py::TestSpssParser`
    - *Methods:* parse_command

### 📄 `pipeline.py`
- ✅ 🏛️ **CompilerPipeline**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_compiler_pipeline.py::TestCompilerPipeline`
    - *Methods:* process, _handle_assignment, _handle_conditional, _handle_file_match, _handle_control_flow, _handle_file_save, _handle_aggregate, analyze_dead_code, process_file, get_variable_version, get_variable_history

### 📄 `previous_pipeline.py`
- ✅ 🏛️ **CompilerPipeline**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_compiler_pipeline.py::TestCompilerPipeline`
    - *Methods:* process, _handle_assignment, _handle_conditional, _handle_file_match, _handle_control_flow, _handle_aggregate, analyze_dead_code, process_file, get_variable_version, get_variable_history

### 📄 `repository.py`
- ✅ 🏛️ **Repository**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_repository.py::TestRepository`
    - *Methods:* scan, list_files, get_content, save_spec, get_spec, get_full_path

### 📄 `runner.py`
- ✅ 🏛️ **PsppRunner**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_runners.py::TestRunners`
    - *Methods:* run_and_probe, _read_first_row

### 📄 `state.py`
- ✅ 🏛️ **VariableVersion**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_data_structures.py::TestDataStructures`
    - *Methods:* id
- ✅ 🏛️ **ClusterMetadata**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_data_structures.py::TestDataStructures`
- ✅ 🏛️ **StateMachine**  <span style='color:green'>Found 1 test(s)</span>
    - 🧪 `tests/unit/test_state.py::TestStateMachine`
    - *Methods:* get_history, get_current_version, register_assignment, register_conditional, register_control_flow, find_dead_versions, _get_current_cluster, register_input_file, register_output_file, reset_scope

---

## 📊 Summary
**Coverage:** 100.0% (23/23 components linked to tests)
