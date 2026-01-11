# 🗺️ Codebase Atlas
> Index of **87** symbols across **27** files.

[TOC]

## 📄 `src/code_forge/R_runner.py`

### M `RRunner.__init__`
- **Line:** 10 (2 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, script_path: str, state_machine)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `dirname`

---
### M `RRunner.run_and_capture`
- **Line:** 14 (46 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, data_file: ?, loader_code: ?)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_generate_wrapper`, `error`, `exists`, `join`, `load`, `open`, `remove`, `run`, `warning`, `write`

---
### M `RRunner._generate_wrapper`
- **Line:** 62 (46 LOC) 
- **Signature:** `(self, output_path: str, data_file: str, loader_code: str)`
- **Called By:**
  - `RRunner.run_and_capture`
- **Calls:** `basename`, `endswith`, `lower`

---
## 📄 `src/code_forge/generator.py`

### M `RGenerator.__init__`
- **Line:** 10 (2 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, state_machine: StateMachine)`
- **Called By:** *None detected* (Entry point?)

---
### M `RGenerator.generate_script`
- **Line:** 15 (44 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, lookups: ?)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_add_header`, `_transpile_node`, `append`, `endswith`, `enumerate`, `join`, `list`, `rstrip`, `set`, `sorted`

---
### M `RGenerator.generate_loader_snippet`
- **Line:** 63 (15 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, event: FileReadEvent)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_generate_loader_block`, `join`

---
### M `RGenerator._transpile_node`
- **Line:** 82 (23 LOC) 
- **Signature:** `(self, node: VariableVersion)`
- **Called By:**
  - `RGenerator.generate_script`
- **Calls:** `group`, `hasattr`, `len`, `lower`, `rstrip`, `search`, `split`, `startswith`, `strip`, `upper`

---
### M `RGenerator.generate_standalone_script`
- **Line:** 108 (8 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, events: ?)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_generate_loader_block`, `append`, `isinstance`, `join`

---
### M `RGenerator._generate_loader_block`
- **Line:** 118 (28 LOC) 
- **Signature:** `(self, event: FileReadEvent)`
- **Called By:**
  - `RGenerator.generate_loader_snippet`
  - `RGenerator.generate_standalone_script`
- **Calls:** `append`, `replace`, `startswith`

---
### M `RGenerator.generate_description`
- **Line:** 148 (8 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, pkg_name: str)`
- **Called By:** *None detected* (Entry point?)

---
### M `RGenerator._add_header`
- **Line:** 158 (5 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `RGenerator.generate_script`
- **Calls:** `append`

---
## 📄 `src/code_forge/optimizer.py`

### M `CodeOptimizer.__init__`
- **Line:** 14 (8 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, project_dir: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_ensure_paths`, `abspath`, `dirname`, `join`

---
### M `CodeOptimizer._ensure_paths`
- **Line:** 24 (10 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `CodeOptimizer.__init__`
- **Calls:** `dirname`, `exists`, `makedirs`, `open`, `write`

---
### M `CodeOptimizer.check_dependencies`
- **Line:** 36 (5 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `CodeOptimizer.optimize_file`
  - `CodeOptimizer.run_linter`
- **Calls:** `warning`, `which`

---
### M `CodeOptimizer.run_linter`
- **Line:** 43 (37 LOC) 
- **Signature:** `(self, relative_path: str)`
- **Called By:**
  - `CodeOptimizer.optimize_file`
- **Calls:** `check_dependencies`, `error`, `exists`, `join`, `run`, `splitlines`, `str`

---
### M `CodeOptimizer.optimize_file`
- **Line:** 83 (24 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, relative_path: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `check_dependencies`, `join`, `run`, `run_linter`, `warning`

---
## 📄 `src/code_forge/refiner.py`

### M `CodeRefiner.__init__`
- **Line:** 13 (2 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, model)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `OllamaClient`

---
### M `CodeRefiner.refine`
- **Line:** 17 (15 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, rough_code: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `format`, `generate`, `info`, `replace`, `strip`, `warning`

---
## 📄 `src/code_forge/rosetta.py`

### M `RosettaStone._split_args`
- **Line:** 28 (25 LOC) 
- **Signature:** `(expression: str)`
- **Called By:**
  - `RosettaStone.translate_expression`
- **Calls:** `append`, `join`, `strip`

---
### M `RosettaStone.translate_expression`
- **Line:** 56 (67 LOC) 🔴 **Long** ⚠️ **Orphan?**
- **Signature:** `(expression: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_split_args`, `find`, `items`, `len`, `range`, `replace`, `sub`, `translate_expression`, `upper`

---
## 📄 `src/common/llm.py`

### M `OllamaClient.__init__`
- **Line:** 9 (8 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, model: str, endpoint: str, timeout: int)`
- **Called By:** *None detected* (Entry point?)

---
### M `OllamaClient.generate`
- **Line:** 19 (32 LOC) 
- **Signature:** `(self, prompt: str, max_tokens: int)`
- **Called By:**
  - `CodeRefiner.refine`
  - `ProjectArchitect.review`
  - `SpecGenerator._describe_node`
  - `SpecGenerator.generate_report`
- **Calls:** `endswith`, `error`, `get`, `json`, `post`, `raise_for_status`, `startswith`, `strip`

---
## 📄 `src/spec_writer/conductor.py`

### M `Conductor.__init__`
- **Line:** 8 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, state_machine: StateMachine)`
- **Called By:** *None detected* (Entry point?)

---
### M `Conductor.identify_clusters`
- **Line:** 11 (17 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `SpecGenerator.generate_report`
- **Calls:** `append`, `range`

---
### M `Conductor._topological_sort`
- **Line:** 30 (7 LOC) 
- **Signature:** `(self, cluster_node_ids: ?)`
- **Called By:**
  - `SpecGenerator.generate_report`

---
### M `Conductor.get_cluster_metadata`
- **Line:** 39 (3 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, cluster_index: int)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `len`

---
## 📄 `src/spec_writer/describer.py`

### M `SpecGenerator.__init__`
- **Line:** 13 (3 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, state_machine: StateMachine, llm_client: OllamaClient)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `Conductor`

---
### M `SpecGenerator.generate_report`
- **Line:** 18 (48 LOC) 
- **Signature:** `(self, dead_ids: ?, runtime_values: ?)`
- **Called By:**
  - `SpecOrchestrator.generate_comprehensive_spec`
- **Calls:** `_describe_node`, `_find_node_by_id`, `_get_node_source`, `_topological_sort`, `append`, `enumerate`, `format`, `generate`, `identify_clusters`, `join`

---
### M `SpecGenerator._find_node_by_id`
- **Line:** 68 (4 LOC) 
- **Signature:** `(self, node_id: str)`
- **Called By:**
  - `SpecGenerator._get_node_source`
  - `SpecGenerator.generate_report`

---
### M `SpecGenerator._get_node_source`
- **Line:** 74 (2 LOC) 
- **Signature:** `(self, node_id: str)`
- **Called By:**
  - `SpecGenerator.generate_report`
- **Calls:** `_find_node_by_id`

---
### M `SpecGenerator._describe_node`
- **Line:** 78 (2 LOC) 
- **Signature:** `(self, node: VariableVersion)`
- **Called By:**
  - `SpecGenerator.generate_report`
- **Calls:** `format`, `generate`, `strip`

---
## 📄 `src/spec_writer/graph.py`

### M `GraphGenerator.__init__`
- **Line:** 10 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, state_machine: StateMachine)`
- **Called By:** *None detected* (Entry point?)

---
### M `GraphGenerator._sanitize_label`
- **Line:** 13 (1 LOC) 
- **Signature:** `(self, label: str)`
- **Called By:**
  - `GraphGenerator.generate_dot`
- **Calls:** `replace`

---
### M `GraphGenerator.generate_dot`
- **Line:** 16 (36 LOC) 
- **Signature:** `(self, highlight_dead: ?)`
- **Called By:**
  - `GraphGenerator.render`
- **Calls:** `_sanitize_label`, `append`, `isinstance`, `join`, `str`, `upper`

---
### M `GraphGenerator.render`
- **Line:** 54 (16 LOC) 
- **Signature:** `(self, output_path: str)`
- **Called By:**
  - `SpecOrchestrator.generate_comprehensive_spec`
- **Calls:** `Source`, `debug`, `generate_dot`, `info`, `render`

---
## 📄 `src/spec_writer/orchestrator.py`

### M `SpecOrchestrator.__init__`
- **Line:** 13 (3 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, llm_client: ?)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `CompilerPipeline`, `OllamaClient`

---
### M `SpecOrchestrator.ingest`
- **Line:** 18 (5 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, file_path: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `SpecGenerator`, `basename`, `info`, `process_file`

---
### M `SpecOrchestrator.generate_comprehensive_spec`
- **Line:** 25 (30 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, output_dir: str, filename_root: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `GraphGenerator`, `ValueError`, `analyze_dead_code`, `generate_report`, `info`, `join`, `makedirs`, `open`, `render`, `write`

---
## 📄 `src/spec_writer/review.py`

### M `ProjectArchitect.__init__`
- **Line:** 24 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, client: OllamaClient)`
- **Called By:** *None detected* (Entry point?)

---
### M `ProjectArchitect.review`
- **Line:** 27 (22 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, r_code: str, spec_content: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_summarize_spec`, `error`, `format`, `generate`, `info`

---
### M `ProjectArchitect._summarize_spec`
- **Line:** 51 (7 LOC) 
- **Signature:** `(self, full_spec: str)`
- **Called By:**
  - `ProjectArchitect.review`
- **Calls:** `append`, `join`, `split`, `startswith`, `strip`

---
## 📄 `src/spss_engine/extractor.py`

### M `AssignmentExtractor._normalize`
- **Line:** 11 (1 LOC) 
- **Signature:** `(name: str)`
- **Called By:**
  - `AssignmentExtractor.extract_target`
- **Calls:** `strip`, `upper`

---
### M `AssignmentExtractor.extract_target`
- **Line:** 22 (38 LOC) 
- **Signature:** `(command: str)`
- **Called By:**
  - `CommandTransformer.transform`
- **Calls:** `_normalize`, `extract_target`, `group`, `match`, `search`, `startswith`, `strip`, `upper`

---
### M `AssignmentExtractor.extract_dependencies`
- **Line:** 63 (43 LOC) 
- **Signature:** `(expression: str)`
- **Called By:**
  - `CommandTransformer.transform`
- **Calls:** `append`, `findall`, `list`, `set`, `strip`, `sub`, `upper`

---
### M `AssignmentExtractor.extract_file_target`
- **Line:** 121 (18 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, command: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `group`, `search`

---
## 📄 `src/spss_engine/inspector.py`

### M `SourceInspector.__init__`
- **Line:** 10 (6 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `SpssLexer`, `SpssParser`, `compile`

---
### M `SourceInspector.scan`
- **Line:** 18 (18 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, code: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `_extract_filenames`, `extend`, `list`, `parse_command`, `set`, `sorted`, `split_commands`

---
### M `SourceInspector._extract_filenames`
- **Line:** 38 (3 LOC) 
- **Signature:** `(self, command_text: str)`
- **Called By:**
  - `SourceInspector.scan`
- **Calls:** `findall`

---
## 📄 `src/spss_engine/lexer.py`

### M `SpssLexer.__init__`
- **Line:** 11 (2 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, raw_text: str)`
- **Called By:** *None detected* (Entry point?)

---
### M `SpssLexer.split_commands`
- **Line:** 15 (47 LOC) 
- **Signature:** `(self, text: str)`
- **Called By:**
  - `CompilerPipeline.process`
  - `SourceInspector.scan`
  - `SpssLexer.get_commands`
- **Calls:** `ValueError`, `append`, `endswith`, `join`, `splitlines`, `strip`

---
### M `SpssLexer.get_commands`
- **Line:** 65 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `split_commands`

---
### M `SpssLexer.normalize_command`
- **Line:** 68 (4 LOC) 
- **Signature:** `(self, command: str)`
- **Called By:**
  - `CompilerPipeline.process`
- **Calls:** `strip`, `sub`

---
## 📄 `src/spss_engine/parser.py`

### M `SpssParser.parse_command`
- **Line:** 21 (28 LOC) 
- **Signature:** `(self, command: str)`
- **Called By:**
  - `CompilerPipeline.process`
  - `SourceInspector.scan`
- **Calls:** `ParsedCommand`, `any`, `startswith`, `strip`, `upper`

---
## 📄 `src/spss_engine/parsers/data_loader.py`

### M `DataLoaderParser.parse`
- **Line:** 5 (41 LOC) 
- **Signature:** `(self, raw_command: str)`
- **Called By:**
  - `CommandTransformer.transform`
- **Calls:** `FileReadEvent`, `compile`, `endswith`, `findall`, `group`, `int`, `search`, `strip`

---
## 📄 `src/spss_engine/pipeline.py`

### M `CompilerPipeline.__init__`
- **Line:** 16 (8 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `AssignmentExtractor`, `CommandTransformer`, `SpssLexer`, `SpssParser`, `StateMachine`

---
### M `CompilerPipeline.process`
- **Line:** 27 (9 LOC) 
- **Signature:** `(self, code: str)`
- **Called By:**
  - `CompilerPipeline.process_file`
- **Calls:** `_apply_event`, `normalize_command`, `parse_command`, `split_commands`, `transform`

---
### M `CompilerPipeline._apply_event`
- **Line:** 38 (35 LOC) 
- **Signature:** `(self, event: SemanticEvent)`
- **Called By:**
  - `CompilerPipeline.process`
- **Calls:** `_get_current_cluster`, `append`, `get_current_version`, `isinstance`, `register_assignment`, `register_conditional`, `register_control_flow`, `register_input_file`, `register_output_file`, `reset_scope`

---
### M `CompilerPipeline.get_variable_version`
- **Line:** 76 (4 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, var_name: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `get_current_version`

---
### M `CompilerPipeline.get_variable_history`
- **Line:** 82 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, var_name: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `get_history`

---
### M `CompilerPipeline.analyze_dead_code`
- **Line:** 85 (2 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `SpecOrchestrator.generate_comprehensive_spec`
- **Calls:** `find_dead_versions`

---
### M `CompilerPipeline.process_file`
- **Line:** 89 (5 LOC) 
- **Signature:** `(self, file_path: str)`
- **Called By:**
  - `SpecOrchestrator.ingest`
- **Calls:** `FileNotFoundError`, `exists`, `open`, `process`, `read`

---
## 📄 `src/spss_engine/repository.py`

### M `Repository.__init__`
- **Line:** 12 (6 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, root_path: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `FileNotFoundError`, `abspath`, `exists`

---
### M `Repository.scan`
- **Line:** 20 (24 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `clear`, `join`, `lower`, `open`, `read`, `relpath`, `replace`, `splitext`, `walk`

---
### M `Repository.list_files`
- **Line:** 46 (2 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `keys`, `list`, `sorted`

---
### M `Repository.get_content`
- **Line:** 50 (3 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, relative_path: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `get`, `replace`

---
### M `Repository.save_spec`
- **Line:** 55 (5 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, relative_path: str, spec_content: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `ValueError`, `replace`

---
### M `Repository.get_spec`
- **Line:** 62 (3 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, relative_path: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `get`, `replace`

---
### M `Repository.get_full_path`
- **Line:** 68 (7 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, relative_path: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `join`, `replace`

---
## 📄 `src/spss_engine/spss_runner.py`

### M `PsppRunner.__init__`
- **Line:** 16 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self, executable: str)`
- **Called By:** *None detected* (Entry point?)

---
### M `PsppRunner.run_and_probe`
- **Line:** 20 (59 LOC) 🔴 **Long** ⚠️ **Orphan?**
- **Signature:** `(self, file_path: str, output_dir: str)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `FileNotFoundError`, `RuntimeError`, `_read_first_row`, `abspath`, `basename`, `dirname`, `error`, `exists`, `info`, `join`

---
### M `PsppRunner._read_first_row`
- **Line:** 83 (17 LOC) 
- **Signature:** `(self, csv_path: str)`
- **Called By:**
  - `PsppRunner.run_and_probe`
- **Calls:** `DictReader`, `exists`, `items`, `next`, `open`, `strip`, `upper`

---
## 📄 `src/spss_engine/state.py`

### M `VariableVersion.id`
- **Line:** 13 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)

---
### M `VariableVersion.__str__`
- **Line:** 17 (1 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)

---
### M `StateMachine.__init__`
- **Line:** 28 (7 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `ClusterMetadata`

---
### M `StateMachine.get_history`
- **Line:** 37 (1 LOC) 
- **Signature:** `(self, var_name: str)`
- **Called By:**
  - `CompilerPipeline.get_variable_history`
  - `StateMachine.get_current_version`
  - `StateMachine.register_assignment`
- **Calls:** `get`, `upper`

---
### M `StateMachine.get_current_version`
- **Line:** 40 (4 LOC) 
- **Signature:** `(self, var_name: str)`
- **Called By:**
  - `CompilerPipeline._apply_event`
  - `CompilerPipeline.get_variable_version`
- **Calls:** `ValueError`, `get_history`

---
### M `StateMachine.register_assignment`
- **Line:** 46 (21 LOC) 
- **Signature:** `(self, var_name: str, source: str, dependencies: ?)`
- **Called By:**
  - `CompilerPipeline._apply_event`
- **Calls:** `VariableVersion`, `_get_current_cluster`, `append`, `get_history`, `len`, `upper`

---
### M `StateMachine.register_conditional`
- **Line:** 69 (1 LOC) 
- **Signature:** `(self, command: str)`
- **Called By:**
  - `CompilerPipeline._apply_event`
- **Calls:** `append`

---
### M `StateMachine.register_control_flow`
- **Line:** 72 (1 LOC) 
- **Signature:** `(self, command: str)`
- **Called By:**
  - `CompilerPipeline._apply_event`
- **Calls:** `append`

---
### M `StateMachine.find_dead_versions`
- **Line:** 75 (10 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `CompilerPipeline.analyze_dead_code`
- **Calls:** `append`, `enumerate`, `items`, `len`

---
### M `StateMachine._get_current_cluster`
- **Line:** 87 (1 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `CompilerPipeline._apply_event`
  - `StateMachine.register_assignment`
  - `StateMachine.register_input_file`
  - `StateMachine.register_output_file`
  - `StateMachine.reset_scope`

---
### M `StateMachine.register_input_file`
- **Line:** 90 (2 LOC) 
- **Signature:** `(self, filename: str)`
- **Called By:**
  - `CompilerPipeline._apply_event`
- **Calls:** `_get_current_cluster`, `add`, `strip`

---
### M `StateMachine.register_output_file`
- **Line:** 94 (2 LOC) 
- **Signature:** `(self, filename: str)`
- **Called By:**
  - `CompilerPipeline._apply_event`
- **Calls:** `_get_current_cluster`, `add`, `strip`

---
### M `StateMachine.reset_scope`
- **Line:** 98 (21 LOC) 
- **Signature:** `(self)`
- **Called By:**
  - `CompilerPipeline._apply_event`
- **Calls:** `ClusterMetadata`, `_get_current_cluster`, `append`, `clear`, `len`

---
## 📄 `src/spss_engine/transformer.py`

### M `CommandTransformer.__init__`
- **Line:** 12 (7 LOC) ⚠️ **Orphan?**
- **Signature:** `(self)`
- **Called By:** *None detected* (Entry point?)
- **Calls:** `AssignmentExtractor`, `DataLoaderParser`, `compile`

---
### M `CommandTransformer._clean_filename`
- **Line:** 21 (4 LOC) 
- **Signature:** `(self, match)`
- **Called By:**
  - `CommandTransformer.transform`
- **Calls:** `group`, `rstrip`

---
### M `CommandTransformer.transform`
- **Line:** 27 (61 LOC) 🔴 **Long**
- **Signature:** `(self, command: ParsedCommand)`
- **Called By:**
  - `CompilerPipeline.process`
- **Calls:** `AssignmentEvent`, `FileMatchEvent`, `FileSaveEvent`, `ScopeResetEvent`, `_clean_filename`, `append`, `extract_dependencies`, `extract_target`, `findall`, `group`

---
