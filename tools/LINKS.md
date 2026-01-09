# 🔗 Codebase Call Graph
**Root:** `/home/jonny/git/state_machine/src`

> ➡️ Indicates a function call made by the definition.

## 📦 Package: `src`
## 📦 Package: `src/common`

### 📄 `llm.py`
- 🏛️ **Class** `OllamaClient`
    - def `__init__`
        - *No outgoing calls detected*
    - def `generate`
        - ex `requests.post`
        - ex `response.raise_for_status`
        - ex `response.json.get.strip`
        - ex `response.json.get`
        - ex `response.json`
        - ex `text.startswith`
        - ex `text.endswith`
        - ex `logger.error`

---
## 📦 Package: `src/spec_writer`

### 📄 `conductor.py`
- 🏛️ **Class** `Conductor`
    - def `__init__`
        - *No outgoing calls detected*
    - def `identify_clusters`
        - ➡️ `range`
        - ➡️ `append`
    - def `_topological_sort`
        - *No outgoing calls detected*
    - def `get_cluster_metadata`
        - ➡️ `len`

---

### 📄 `describer.py`
- 🏛️ **Class** `SpecGenerator`
    - def `__init__`
        - ➡️ `Conductor`
    - def `generate_report`
        - 🔄 `self.conductor.identify_clusters`
        - ➡️ `enumerate`
        - ➡️ `join`
        - 🔄 `self._get_node_source`
        - ex `GENERATE_TITLE_PROMPT.format`
        - 🔄 `self.llm_client.generate.strip`
        - 🔄 `self.llm_client.generate`
        - ex `report_parts.append`
        - 🔄 `self.conductor._topological_sort`
        - 🔄 `self._find_node_by_id`
        - 🔄 `self._describe_node`
        - ex `node.source.strip`
    - def `_find_node_by_id`
        - *No outgoing calls detected*
    - def `_get_node_source`
        - 🔄 `self._find_node_by_id`
    - def `_describe_node`
        - ex `DESCRIBE_NODE_PROMPT.format`
        - 🔄 `self.llm_client.generate.strip`
        - 🔄 `self.llm_client.generate`

---

### 📄 `graph.py`
- 🏛️ **Class** `GraphGenerator`
    - def `__init__`
        - *No outgoing calls detected*
    - def `_sanitize_label`
        - ex `label.replace.replace`
        - ex `label.replace`
    - def `generate_dot`
        - ex `dot.append`
        - 🔄 `self._sanitize_label`
        - ➡️ `isinstance`
        - ex `str.upper`
        - ➡️ `str`
        - ➡️ `join`
    - def `render`
        - 🔄 `self.generate_dot`
        - ex `graphviz.Source`
        - ex `src.render`
        - ex `logger.info`
        - ex `logger.debug`

---

### 📄 `orchestrator.py`
- 🏛️ **Class** `SpecOrchestrator`
    - def `__init__`
        - ➡️ `CompilerPipeline`
        - ➡️ `OllamaClient`
    - def `ingest`
        - ex `logger.info`
        - ex `os.path.basename`
        - 🔄 `self.pipeline.process_file`
        - ➡️ `SpecGenerator`
    - def `generate_comprehensive_spec`
        - ➡️ `ValueError`
        - 🔄 `self.pipeline.analyze_dead_code`
        - ➡️ `GraphGenerator`
        - ex `os.path.join`
        - ex `logger.info`
        - ex `graph_gen.render`
        - 🔄 `self.generator.generate_report`
        - ex `os.makedirs`
        - ➡️ `open`
        - ex `f.write`

---

### 📄 `review.py`
- 🏛️ **Class** `ProjectArchitect`
    - def `__init__`
        - *No outgoing calls detected*
    - def `review`
        - ex `logger.info`
        - 🔄 `self._summarize_spec`
        - ex `ARCHITECT_PROMPT.format`
        - 🔄 `self.llm.generate`
        - ex `logger.error`
    - def `_summarize_spec`
        - ex `full_spec.split`
        - ex `line.startswith`
        - ex `line.strip.startswith`
        - ex `line.strip`
        - ex `summary.append`
        - ➡️ `join`

---
## 📦 Package: `src/code_forge`

### 📄 `R_runner.py`
- 🏛️ **Class** `RRunner`
    - def `__init__`
        - ex `os.path.dirname`
    - def `run_and_capture`
        - ex `logger.warning`
        - ex `os.path.join`
        - 🔄 `self._generate_wrapper`
        - ➡️ `open`
        - ex `f.write`
        - ex `subprocess.run`
        - ex `logger.error`
        - ex `os.path.exists`
        - ex `json.load`
        - ex `os.remove`
    - def `_generate_wrapper`
        - ex `os.path.basename`
        - ex `data_file.lower.endswith`
        - ex `data_file.lower`

---

### 📄 `generator.py`
- 🏛️ **Class** `RGenerator`
    - def `__init__`
        - *No outgoing calls detected*
    - def `generate_script`
        - 🔄 `self._add_header`
        - 🔄 `self.script_lines.append`
        - ➡️ `join`
        - ex `f.split`
        - ex `lookup_args.append`
        - ➡️ `sorted`
        - ➡️ `list`
        - ➡️ `set`
        - ➡️ `enumerate`
        - 🔄 `self._transpile_node`
        - ex `strip.endswith`
        - ➡️ `strip`
        - ➡️ `rstrip`
    - def `generate_loader_snippet`
        - 🔄 `self._generate_loader_block`
        - ➡️ `join`
    - def `_transpile_node`
        - ➡️ `hasattr`
        - ex `node.source.strip`
        - ex `node.name.lower`
        - ex `expr.upper.startswith`
        - ex `expr.upper`
        - ex `expr.split`
        - ➡️ `len`
        - ex `strip.rstrip.lower`
        - ex `strip.rstrip`
        - ➡️ `strip`
        - ex `re.search`
        - ex `match.group.lower`
        - ex `match.group`
    - def `generate_standalone_script`
        - 🔄 `self.script_lines.append`
        - ➡️ `isinstance`
        - 🔄 `self._generate_loader_block`
        - ➡️ `join`
    - def `_generate_loader_block`
        - ex `raw_delim.replace`
        - ex `raw_qual.replace`
        - 🔄 `self.script_lines.append`
        - ex `spss_type.startswith`
    - def `generate_description`
        - *No outgoing calls detected*
    - def `_add_header`
        - 🔄 `self.script_lines.append`

---

### 📄 `optimizer.py`
- 🏛️ **Class** `CodeOptimizer`
    - def `__init__`
        - ex `os.path.abspath`
        - ex `os.path.join`
        - ex `os.path.dirname`
        - 🔄 `self._ensure_paths`
    - def `_ensure_paths`
        - ex `os.makedirs`
        - ex `os.path.dirname`
        - ex `os.path.exists`
        - ➡️ `open`
        - ex `f.write`
    - def `check_dependencies`
        - ex `shutil.which`
        - ex `logger.warning`
    - def `run_linter`
        - 🔄 `self.check_dependencies`
        - ex `os.path.join`
        - ex `os.path.exists`
        - ex `subprocess.run`
        - ex `logger.error`
        - ex `result.stdout.splitlines`
        - ➡️ `str`
    - def `optimize_file`
        - ex `os.path.join`
        - 🔄 `self.check_dependencies`
        - ex `subprocess.run`
        - ex `logger.warning`
        - 🔄 `self.run_linter`

---

### 📄 `refiner.py`
- 🏛️ **Class** `CodeRefiner`
    - def `__init__`
        - ➡️ `OllamaClient`
    - def `refine`
        - ex `logger.info`
        - ex `REFINE_CODE_PROMPT.format`
        - 🔄 `self.client.generate`
        - ex `refined_code.replace.replace.strip`
        - ex `refined_code.replace.replace`
        - ex `refined_code.replace`
        - ex `logger.warning`

---

### 📄 `rosetta.py`
- 🏛️ **Class** `RosettaStone`
    - def `_split_args`
        - ex `current_arg.append`
        - ex `args.append`
        - ex `join.strip`
        - ➡️ `join`
    - def `translate_expression`
        - ex `expression.replace`
        - ex `re.sub`
        - ex `expr.upper`
        - ex `expr.upper.find`
        - ex `expr.find`
        - ➡️ `range`
        - ➡️ `len`
        - ex `RosettaStone._split_args`
        - ex `RosettaStone.translate_expression`
        - ex `expr.replace`
        - ex `RosettaStone.TRANSLATIONS.items`

---
## 📦 Package: `src/spss_engine`

### 📄 `extractor.py`
- 🏛️ **Class** `AssignmentExtractor`
    - def `_normalize`
        - ex `name.strip.upper`
        - ex `name.strip`
    - def `extract_target`
        - ex `command.strip`
        - ex `re.match`
        - ex `AssignmentExtractor.extract_target`
        - ex `if_match.group`
        - ex `AssignmentExtractor._normalize`
        - ex `compute_match.group`
        - ex `cmd.upper`
        - ex `re.search`
        - ex `recode_into_match.group`
        - ex `cmd.upper.startswith`
        - ex `recode_match.group`
        - ex `decl_match.group`
    - def `extract_dependencies`
        - ex `re.sub`
        - ex `re.findall`
        - ex `token.strip.upper`
        - ex `token.strip`
        - ex `dependencies.append`
        - ➡️ `list`
        - ➡️ `set`
    - def `extract_file_target`
        - ex `re.search`
        - ex `match.group`
    - def `extract_file_target`
        - ex `re.search`
        - ex `match.group`

---

### 📄 `inspector.py`
- 🏛️ **Class** `SourceInspector`
    - def `__init__`
        - ➡️ `SpssLexer`
        - ➡️ `SpssParser`
        - ex `re.compile`
    - def `scan`
        - 🔄 `self.lexer.split_commands`
        - 🔄 `self.parser.parse_command`
        - 🔄 `self._extract_filenames`
        - ex `inputs.extend`
        - ex `outputs.extend`
        - ➡️ `sorted`
        - ➡️ `list`
        - ➡️ `set`
    - def `_extract_filenames`
        - 🔄 `self._ARG_PATTERN.findall`

---

### 📄 `lexer.py`
- 🏛️ **Class** `SpssLexer`
    - def `__init__`
        - *No outgoing calls detected*
    - def `split_commands`
        - ➡️ `ValueError`
        - ex `target_text.splitlines`
        - ex `line.strip`
        - ex `current_command.append`
        - ex `stripped_line.endswith`
        - ➡️ `join`
        - ex `commands.append`
    - def `get_commands`
        - 🔄 `self.split_commands`
    - def `normalize_command`
        - ex `re.sub.strip`
        - ex `re.sub`

---

### 📄 `parser.py`
- 🏛️ **Class** `SpssParser`
    - def `parse_command`
        - ex `command.strip.upper`
        - ex `command.strip`
        - ex `cmd_upper.startswith`
        - ➡️ `ParsedCommand`
        - ➡️ `any`

---

### 📄 `pipeline.py`
- 🏛️ **Class** `CompilerPipeline`
    - def `__init__`
        - ➡️ `StateMachine`
        - ➡️ `SpssParser`
        - ➡️ `SpssLexer`
        - ➡️ `CommandTransformer`
        - ➡️ `AssignmentExtractor`
    - def `process`
        - 🔄 `self.lexer.split_commands`
        - 🔄 `self.lexer.normalize_command`
        - 🔄 `self.parser.parse_command`
        - 🔄 `self.transformer.transform`
        - 🔄 `self._apply_event`
    - def `_apply_event`
        - ➡️ `isinstance`
        - 🔄 `self.state._get_current_cluster`
        - 🔄 `self.state.reset_scope`
        - 🔄 `self.state.register_input_file`
        - 🔄 `self.state.register_output_file`
        - 🔄 `self.state.register_control_flow`
        - 🔄 `self.state.register_assignment`
        - 🔄 `self.state.get_current_version`
        - ex `resolved_deps.append`
        - ex `event.source_command.upper.startswith`
        - ex `event.source_command.upper`
        - 🔄 `self.state.register_conditional`
    - def `get_variable_version`
        - 🔄 `self.state.get_current_version`
    - def `get_variable_history`
        - 🔄 `self.state.get_history`
    - def `analyze_dead_code`
        - 🔄 `self.state.find_dead_versions`
    - def `process_file`
        - ex `os.path.exists`
        - ➡️ `FileNotFoundError`
        - ➡️ `open`
        - 🔄 `self.process`
        - ex `f.read`

---

### 📄 `previous_pipeline.py`
- 🏛️ **Class** `CompilerPipeline`
    - def `__init__`
        - ➡️ `SpssParser`
        - ➡️ `AssignmentExtractor`
        - ➡️ `StateMachine`
    - def `process`
        - ➡️ `SpssLexer`
        - ex `lexer.get_commands`
        - 🔄 `self.parser.parse_command`
        - 🔄 `self.dispatch_table.get`
        - ➡️ `handler`
    - def `_handle_assignment`
        - 🔄 `self.extractor.extract_target`
        - 🔄 `self.extractor.extract_dependencies`
        - ex `dep_name.upper`
        - ex `target_var.upper`
        - 🔄 `self.state_machine.get_current_version`
        - ex `resolved_deps.append`
        - 🔄 `self.state_machine.register_assignment`
    - def `_handle_conditional`
        - 🔄 `self.state_machine.register_conditional`
        - 🔄 `self.extractor.extract_target`
        - 🔄 `self._handle_assignment`
    - def `_handle_file_match`
        - 🔄 `self.state_machine.register_assignment`
    - def `_handle_control_flow`
        - 🔄 `self.state_machine.register_control_flow`
    - def `_handle_aggregate`
        - ex `re.findall`
        - ex `re.search`
        - ex `break_match.group.split`
        - ex `break_match.group`
        - ex `deps.append`
        - 🔄 `self.state_machine.get_current_version`
        - ex `target.upper`
        - 🔄 `self.state_machine.register_assignment`
    - def `analyze_dead_code`
        - 🔄 `self.state_machine.find_dead_versions`
    - def `process_file`
        - ex `os.path.exists`
        - ➡️ `FileNotFoundError`
        - ➡️ `open`
        - 🔄 `self.process`
        - ex `f.read`
    - def `get_variable_version`
        - 🔄 `self.state_machine.get_history`
    - def `get_variable_history`
        - 🔄 `self.state_machine.get_history`

---

### 📄 `repository.py`
- 🏛️ **Class** `Repository`
    - def `__init__`
        - ex `os.path.exists`
        - ➡️ `FileNotFoundError`
        - ex `os.path.abspath`
    - def `scan`
        - 🔄 `self._files.clear`
        - ex `os.walk`
        - ➡️ `lower`
        - ex `os.path.splitext`
        - ex `os.path.join`
        - ex `os.path.relpath`
        - ex `rel_path.replace`
        - ➡️ `open`
        - ex `f.read`
    - def `list_files`
        - ➡️ `sorted`
        - ➡️ `list`
        - 🔄 `self._files.keys`
    - def `get_content`
        - ex `relative_path.replace`
        - 🔄 `self._files.get`
    - def `save_spec`
        - ex `relative_path.replace`
        - ➡️ `ValueError`
    - def `get_spec`
        - ex `relative_path.replace`
        - 🔄 `self._specs.get`
    - def `get_full_path`
        - ex `relative_path.replace`
        - ex `os.path.join`

---

### 📄 `spss_runner.py`
- 🏛️ **Class** `PsppRunner`
    - def `__init__`
        - *No outgoing calls detected*
    - def `run_and_probe`
        - ex `os.path.exists`
        - ➡️ `FileNotFoundError`
        - ex `os.path.abspath`
        - ex `os.path.dirname`
        - ex `os.path.splitext`
        - ex `os.path.basename`
        - ex `os.path.join`
        - ➡️ `open`
        - ex `f.read`
        - ex `csv_path.replace`
        - ex `f.write`
        - ex `subprocess.run`
        - ex `logger.info`
        - ex `logger.error`
        - ➡️ `RuntimeError`
        - ex `os.remove`
        - 🔄 `self._read_first_row`
    - def `_read_first_row`
        - ex `os.path.exists`
        - ➡️ `open`
        - ex `csv.DictReader`
        - ➡️ `next`
        - ex `k.strip.upper`
        - ex `k.strip`
        - ex `row.items`

---

### 📄 `state.py`
- 🏛️ **Class** `VariableVersion`
    - def `id`
        - *No outgoing calls detected*
    - def `__str__`
        - *No outgoing calls detected*
- 🏛️ **Class** `StateMachine`
    - def `__init__`
        - ➡️ `ClusterMetadata`
    - def `get_history`
        - 🔄 `self.history_ledger.get`
        - ex `var_name.upper`
    - def `get_current_version`
        - 🔄 `self.get_history`
        - ➡️ `ValueError`
    - def `register_assignment`
        - ex `var_name.upper`
        - 🔄 `self.get_history`
        - ➡️ `len`
        - ➡️ `VariableVersion`
        - ➡️ `append`
        - 🔄 `self.nodes.append`
        - 🔄 `self._get_current_cluster`
    - def `register_conditional`
        - 🔄 `self.conditionals.append`
    - def `register_control_flow`
        - 🔄 `self.control_flow.append`
    - def `find_dead_versions`
        - 🔄 `self.history_ledger.items`
        - ➡️ `enumerate`
        - ➡️ `len`
        - ex `dead_ids.append`
    - def `_get_current_cluster`
        - *No outgoing calls detected*
    - def `register_input_file`
        - ex `filename.strip.strip.strip`
        - ex `filename.strip.strip`
        - ex `filename.strip`
        - 🔄 `self._get_current_cluster.inputs.add`
        - 🔄 `self._get_current_cluster`
    - def `register_output_file`
        - ex `filename.strip.strip.strip`
        - ex `filename.strip.strip`
        - ex `filename.strip`
        - 🔄 `self._get_current_cluster.outputs.add`
        - 🔄 `self._get_current_cluster`
    - def `reset_scope`
        - 🔄 `self._get_current_cluster`
        - ➡️ `len`
        - 🔄 `self.history_ledger.clear`
        - 🔄 `self.clusters.append`
        - ➡️ `ClusterMetadata`

---

### 📄 `transformer.py`
- 🏛️ **Class** `CommandTransformer`
    - def `__init__`
        - ➡️ `AssignmentExtractor`
        - ➡️ `DataLoaderParser`
        - ex `re.compile`
    - def `_clean_filename`
        - ex `match.group`
        - ex `match.group.rstrip`
    - def `transform`
        - 🔄 `self.data_loader.parse`
        - ex `events.append`
        - ➡️ `ScopeResetEvent`
        - 🔄 `self.re_file_arg.findall`
        - ex `unquoted.rstrip`
        - ex `files.append`
        - ➡️ `FileMatchEvent`
        - 🔄 `self.re_file_arg.search`
        - 🔄 `self._clean_filename`
        - ➡️ `FileSaveEvent`
        - 🔄 `self.extractor.extract_target`
        - 🔄 `self.extractor.extract_dependencies`
        - ex `d.upper`
        - ex `target.upper`
        - ➡️ `AssignmentEvent`
        - 🔄 `self.re_break.search`
        - ex `break_match.group.split`
        - ex `break_match.group`
        - 🔄 `self.re_agg_targets.findall`
        - ex `t.upper`

---
## 📦 Package: `src/spss_engine/parsers`

### 📄 `data_loader.py`
- 🏛️ **Class** `DataLoaderParser`
    - def `parse`
        - ex `raw_command.strip`
        - ex `re.search`
        - ex `file_match.group`
        - ex `delim_match.group`
        - ex `qual_match.group`
        - ➡️ `int`
        - ex `first_case_match.group`
        - ex `var_block_match.group.strip`
        - ex `var_block_match.group`
        - ex `block.endswith`
        - ex `re.compile`
        - ex `schema_pattern.findall`
        - ➡️ `FileReadEvent`

---
