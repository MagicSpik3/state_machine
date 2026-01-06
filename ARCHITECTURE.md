# 🗺️ Codebase Architecture Map
**Root:** `/home/jonny/git/state_machine/src`

## 📦 Package: `src`

### 📄 `__init__.py`

---
## 📦 Package: `src/spec_writer`

### 📄 `__init__.py`

---

### 📄 `conductor.py`
**Imports:**
- `from collections import defaultdict`
- `from collections import deque`
- `from spss_engine.state import StateMachine`
- `from typing import Dict`
- `from typing import List`
- `from typing import Set`

**Definitions:**
- 🏛️ **Class** `Conductor`
    - `def __init__(...)`
    - `def _build_graph(...)`
    - `def identify_clusters(...)`
    - `def _bfs_cluster(...)`
    - `def _topological_sort(...)`

---

### 📄 `describer.py`
**Imports:**
- `from abc import ABC`
- `from abc import abstractmethod`
- `from spec_writer.conductor import Conductor`
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import Dict`
- `from typing import List`
- `import json`
- `import logging`
- `import requests`

**Definitions:**
- 🏛️ **Class** `LLMClient`
    - `def describe_node(...)`
    - `def generate_title(...)`
- 🏛️ **Class** `MockLLM`
    - `def describe_node(...)`
    - `def generate_title(...)`
- 🏛️ **Class** `OllamaClient`
    - `def __init__(...)`
    - `def _call_ollama(...)`
    - `def describe_node(...)`
    - `def generate_title(...)`
- 🏛️ **Class** `SpecGenerator`
    - `def __init__(...)`
    - `def generate_report(...)`
    - `def _find_version(...)`

---

### 📄 `graph.py`
**Imports:**
- `from spss_engine.state import StateMachine`
- `from typing import List`
- `from typing import Optional`
- `import graphviz`

**Definitions:**
- 🏛️ **Class** `GraphGenerator`
    - `def generate_dot(...)`
    - `def render(...)`

---
## 📦 Package: `src/code_forge`

### 📄 `__init__.py`

---

### 📄 `generator.py`
**Imports:**
- `from spss_engine.state import StateMachine`
- `from spss_engine.state import VariableVersion`
- `from typing import Dict`
- `from typing import List`
- `from typing import Set`
- `import re`

**Definitions:**
- 🏛️ **Class** `RGenerator`
    - `def __init__(...)`
    - `def generate_description(...)`
    - `def generate_script(...)`
    - `def _analyze_contract(...)`
    - `def _topological_sort(...)`
    - `def _transpile_node(...)`

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
- `import re`

**Definitions:**
- 🏛️ **Class** `TokenType`
- 🏛️ **Class** `ParsedStatement`
- 🏛️ **Class** `SpssParser`
    - `def __init__(...)`
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
- `from typing import List`
- `from typing import Optional`
- `import os`
- `import re`

**Definitions:**
- 🏛️ **Class** `CompilerPipeline`
    - `def __init__(...)`
    - `def process(...)`
    - `def _handle_assignment(...)`
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

### 📄 `runner.py`
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
- `from typing import Tuple`

**Definitions:**
- 🏛️ **Class** `VariableVersion`
- 🏛️ **Class** `StateMachine`
    - `def __init__(...)`
    - `def _normalize(...)`
    - `def get_current_version(...)`
    - `def get_history(...)`
    - `def register_assignment(...)`
    - `def register_conditional(...)`
    - `def register_control_flow(...)`
    - `def register_file_save(...)`
    - `def register_file_match(...)`
    - `def find_dead_versions(...)`

---
