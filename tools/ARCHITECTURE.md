# 🗺️ Codebase Architecture Map
**Root:** `/home/jonny/git/state_machine/src`

## 📦 Package: `src`

### 📄 `__init__.py`

---
## 📦 Package: `src/common`

### 📄 `__init__.py`

---

### 📄 `llm.py`
**Imports:**
- `from typing import Optional`
- `import logging`
- `import requests`

**Definitions:**
- 🏛️ **Class** `OllamaClient`
    - `def __init__(...)`
    - `def generate(...)`

---

### 📄 `prompts.py`

---
## 📦 Package: `src/spec_writer`

### 📄 `__init__.py`

---

### 📄 `conductor.py`
**Imports:**
- `from spss_engine.state import ClusterMetadata`
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `from typing import Set`

**Definitions:**
- 🏛️ **Class** `Conductor`
    - `def __init__(...)`
    - `def identify_clusters(...)`
    - `def _topological_sort(...)`
    - `def get_cluster_metadata(...)`

---

### 📄 `describer.py`
**Imports:**
- `from common.llm import OllamaClient`
- `from spec_writer.conductor import Conductor`
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `import logging`

**Definitions:**
- 🏛️ **Class** `SpecGenerator`
    - `def __init__(...)`
    - `def generate_report(...)`
    - `def _find_node_by_id(...)`
    - `def _get_node_source(...)`
    - `def _describe_node(...)`

---

### 📄 `graph.py`
**Imports:**
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import List`
- `from typing import Optional`
- `import graphviz`
- `import logging`
- `import os`

**Definitions:**
- 🏛️ **Class** `GraphGenerator`
    - `def __init__(...)`
    - `def _sanitize_label(...)`
    - `def generate_dot(...)`
    - `def render(...)`

---

### 📄 `orchestrator.py`
**Imports:**
- `from common.llm import OllamaClient`
- `from spec_writer.describer import SpecGenerator`
- `from spec_writer.graph import GraphGenerator`
- `from spec_writer.review import ProjectArchitect`
- `from spss_engine.pipeline import CompilerPipeline`
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `import logging`
- `import os`

**Definitions:**
- 🏛️ **Class** `SpecOrchestrator`
    - `def __init__(...)`
    - `def ingest(...)`
    - `def generate_comprehensive_spec(...)`

---

### 📄 `review.py`
**Imports:**
- `from common.llm import OllamaClient`
- `from typing import Dict`
- `from typing import List`
- `import logging`
- `import re`

**Definitions:**
- 🏛️ **Class** `ProjectArchitect`
    - `def __init__(...)`
    - `def review(...)`
    - `def _summarize_spec(...)`

---
## 📦 Package: `src/code_forge`

### 📄 `R_runner.py`
**Imports:**
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `import csv`
- `import logging`
- `import os`
- `import pandas`
- `import subprocess`

**Definitions:**
- 🏛️ **Class** `RRunner`
    - `def __init__(...)`
    - `def run_and_capture(...)`
    - `def _read_first_row(...)`

---

### 📄 `__init__.py`

---

### 📄 `generator.py`
**Imports:**
- `from code_forge.rosetta import RosettaStone`
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import List`
- `from typing import Set`
- `import re`

**Definitions:**
- 🏛️ **Class** `RGenerator`
    - `def __init__(...)`
    - `def generate_description(...)`
    - `def _get_join_blocks(...)`
    - `def generate_script(...)`
    - `def _transpile_node(...)`
    - `def _topological_sort(...)`
    - `def _analyze_contract(...)`
    - `def _transpile_node(...)`
    - `def _topological_sort(...)`
    - `def _analyze_contract(...)`

---

### 📄 `optimizer.py`
**Imports:**
- `from typing import Any`
- `from typing import Dict`
- `from typing import List`
- `import logging`
- `import os`
- `import shutil`
- `import subprocess`

**Definitions:**
- 🏛️ **Class** `CodeOptimizer`
    - `def __init__(...)`
    - `def _ensure_paths(...)`
    - `def check_dependencies(...)`
    - `def run_linter(...)`
    - `def optimize_file(...)`

---

### 📄 `refiner.py`
**Imports:**
- `from common.llm import OllamaClient`
- `from common.prompts import REFINE_CODE_PROMPT`
- `import logging`

**Definitions:**
- 🏛️ **Class** `CodeRefiner`
    - `def __init__(...)`
    - `def refine(...)`

---

### 📄 `rosetta.py`
**Imports:**
- `from typing import List`
- `import re`

**Definitions:**
- 🏛️ **Class** `RosettaStone`
    - `def _split_args(...)`
    - `def translate_expression(...)`

---
## 📦 Package: `src/spss_engine`

### 📄 `extractor.py`
**Imports:**
- `from typing import List`
- `from typing import Optional`
- `import re`

**Definitions:**
- 🏛️ **Class** `AssignmentExtractor`
    - `def _normalize(...)`
    - `def extract_target(...)`
    - `def extract_dependencies(...)`
    - `def extract_file_target(...)`
    - `def extract_file_target(...)`

---

### 📄 `lexer.py`
**Imports:**
- `from typing import List`
- `import re`

**Definitions:**
- 🏛️ **Class** `SpssLexer`
    - `def __init__(...)`
    - `def get_commands(...)`
    - `def normalize_command(...)`

---

### 📄 `parser.py`
**Imports:**
- `from dataclasses import dataclass`
- `from enum import Enum`
- `from enum import auto`

**Definitions:**
- 🏛️ **Class** `TokenType`
- 🏛️ **Class** `ParsedCommand`
- 🏛️ **Class** `SpssParser`
    - `def parse_command(...)`

---

### 📄 `pipeline.py`
**Imports:**
- `from spss_engine.extractor import AssignmentExtractor`
- `from spss_engine.lexer import SpssLexer`
- `from spss_engine.parser import SpssParser`
- `from spss_engine.parser import TokenType`
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import Callable`
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `import os`
- `import re`

**Definitions:**
- 🏛️ **Class** `CompilerPipeline`
    - `def __init__(...)`
    - `def process(...)`
    - `def _handle_assignment(...)`
    - `def _handle_conditional(...)`
    - `def _handle_file_match(...)`
    - `def _handle_control_flow(...)`
    - `def _handle_file_save(...)`
    - `def _handle_aggregate(...)`
    - `def analyze_dead_code(...)`
    - `def process_file(...)`
    - `def get_variable_version(...)`
    - `def get_variable_history(...)`

---

### 📄 `previous_pipeline.py`
**Imports:**
- `from spss_engine.extractor import AssignmentExtractor`
- `from spss_engine.lexer import SpssLexer`
- `from spss_engine.parser import SpssParser`
- `from spss_engine.parser import TokenType`
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import Callable`
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `import os`
- `import re`

**Definitions:**
- 🏛️ **Class** `CompilerPipeline`
    - `def __init__(...)`
    - `def process(...)`
    - `def _handle_assignment(...)`
    - `def _handle_conditional(...)`
    - `def _handle_file_match(...)`
    - `def _handle_control_flow(...)`
    - `def _handle_aggregate(...)`
    - `def analyze_dead_code(...)`
    - `def process_file(...)`
    - `def get_variable_version(...)`
    - `def get_variable_history(...)`

---

### 📄 `repository.py`
**Imports:**
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `import os`

**Definitions:**
- 🏛️ **Class** `Repository`
    - `def __init__(...)`
    - `def scan(...)`
    - `def list_files(...)`
    - `def get_content(...)`
    - `def save_spec(...)`
    - `def get_spec(...)`
    - `def get_full_path(...)`

---

### 📄 `spss_runner.py`
**Imports:**
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `import csv`
- `import logging`
- `import os`
- `import subprocess`

**Definitions:**
- 🏛️ **Class** `PsppRunner`
    - `def __init__(...)`
    - `def run_and_probe(...)`
    - `def _read_first_row(...)`

---

### 📄 `state.py`
**Imports:**
- `from dataclasses import dataclass`
- `from dataclasses import field`
- `from typing import Dict`
- `from typing import List`
- `from typing import Optional`
- `from typing import Set`

**Definitions:**
- 🏛️ **Class** `VariableVersion`
    - `def id(...)`
- 🏛️ **Class** `ClusterMetadata`
- 🏛️ **Class** `StateMachine`
    - `def __init__(...)`
    - `def get_history(...)`
    - `def get_current_version(...)`
    - `def register_assignment(...)`
    - `def register_conditional(...)`
    - `def register_control_flow(...)`
    - `def find_dead_versions(...)`
    - `def _get_current_cluster(...)`
    - `def register_input_file(...)`
    - `def register_output_file(...)`
    - `def reset_scope(...)`

---
