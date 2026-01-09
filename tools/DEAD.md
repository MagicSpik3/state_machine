# 💀 Dead Code Detector
**Scanning:** `src` + root files

Scanning 29 files...

## 🔍 Potential Dead Code Analysis
> **Note:** This uses a name-based heuristic. If a method is named `run`, and `run` is called anywhere, it is considered alive.
> Items listed below have **ZERO** references found in the codebase (excluding their own definition).

### 📄 `src/spec_writer/orchestrator.py`
- 📦 **SpecOrchestrator** (Line 12)
- 𝑓 **ingest** (Line 18)
- 𝑓 **generate_comprehensive_spec** (Line 25)

### 📄 `src/spec_writer/conductor.py`
- 𝑓 **get_cluster_metadata** (Line 39)

### 📄 `src/code_forge/generator.py`
- 𝑓 **generate_standalone_script** (Line 108)

### 📄 `src/code_forge/optimizer.py`
- 📦 **CodeOptimizer** (Line 10)
- 𝑓 **optimize_file** (Line 83)

### 📄 `src/spss_engine/previous_pipeline.py`
- 𝑓 **get_variable_version** (Line 125)
- 𝑓 **get_variable_history** (Line 131)

### 📄 `src/spss_engine/extractor.py`
- 𝑓 **extract_file_target** (Line 109)
- 𝑓 **extract_file_target** (Line 121)

### 📄 `src/spss_engine/repository.py`
- 𝑓 **get_content** (Line 50)
- 𝑓 **save_spec** (Line 55)
- 𝑓 **get_spec** (Line 62)

### 📄 `src/spss_engine/pipeline.py`
- 𝑓 **get_variable_version** (Line 76)
- 𝑓 **get_variable_history** (Line 82)

---
**Found 16 potential zombies.** 🧟
