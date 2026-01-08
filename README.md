# Statify 🤖📊



> **Turn Legacy SPSS Code into Modern Documentation & R Packages.**

Statify is an intelligent transpiler pipeline that ingests legacy SPSS syntax files (`.sps`), analyzes their logic flow, verifies their behavior against ground truth data (using PSPP), generates human-readable specifications (Markdown), and transpiles them into modern, optimized R packages.

## 🌟 Key Features

* **Logic Extraction:** Parses SPSS syntax into a semantic State Machine (Graph).
* **Visual Flow:** Renders logic flowcharts automatically (Graphviz).
* **Behavioral Verification:** Runs the original code using PSPP to capture "Ground Truth" values.
* **AI Documentation:** Uses LLMs (Ollama) to describe business logic in plain English.
* **R Transpilation:** Generates functionally equivalent R code (using `dplyr`/`haven`).
* **Equivalence Checking:** Verifies the new R code matches the original SPSS outputs.

## 🏗️ Architecture

The system is built on a modular "Assembly Line" architecture:

1.  **Lexer/Parser:** Tokenizes SPSS and builds a semantic model.
2.  **Compiler Pipeline:** detailed static analysis (Dead Code Detection, Dependency Mapping).
3.  **State Machine:** The central source of truth for all variable history.
4.  **Spec Orchestrator:** Coordinates the generation of docs, graphs, and code.
5.  **Code Forge:** The factory for generating and refining R code.

## 🚀 Usage

### Prerequisites
* Python 3.10+
* Graphviz (`sudo apt install graphviz`)
* PSPP (Optional, for verification: `sudo apt install pspp`)
* Ollama (Running locally for AI features)

### Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### Running the CLI

To process a single file or a directory:

```bash
# Basic Documentation
python statify.py legacy_src/ --output docs/

# Full Suite (Docs + R Code + Verification)
python statify.py legacy_src/ --output docs/ --code --refine

```

## 🧪 Testing

The project maintains a rigorous test suite (100+ tests) covering unit logic, component integration, and end-to-end workflows.

```bash
# Run all tests
PYTHONPATH=src:. pytest

# Run specific suite
PYTHONPATH=src:. pytest tests/integration/test_end_to_end.py

```

## 📂 Project Structure

* `src/spss_engine`: Core parsing and state management.
* `src/spec_writer`: Documentation and Graphviz generation.
* `src/code_forge`: R code generation and optimization tools.
* `src/common`: Shared utilities (LLM client).
* `tests`: Comprehensive pytest suite.

```
