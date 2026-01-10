**Assessment by Prof. (Software Engineering / Program Analysis)**
"""
python
from spss_engine.extractor import AssignmentExtractor
from spss_engine.lexer import SpssLexer
from spss_engine.parser import SpssParser, TokenType
from spss_engine.state import StateMachine, VariableVersion
from typing import Callable, Dict, List, Optional
import os
import re

class CompilerPipeline:
    def __init__(self):
        self.state = StateMachine() # Using self.state to match new logic
        self.state_machine = self.state # Alias for backward compatibility if needed
        
        self.parser = SpssParser()
        self.extractor = AssignmentExtractor()
        
        # 🟢 Initialize Lexer (Stateless mode)
        self.lexer = SpssLexer() 
        
        self.join_counter = 0
        self.source_file = None

    def process(self, code: str):
        self.source_file = "script.sps" # Default
        self.state.register_input_file(self.source_file)
        
        # 🟢 Use Stateless Lexer API
        commands = self.lexer.split_commands(code)
        
        for i, command in enumerate(commands):
            # Normalize and Parse
            normalized = self.lexer.normalize_command(command)
            parsed = self.parser.parse_command(normalized)
            
            # --- CLUSTER SEPARATION LOGIC ---
            # 🟢 FIX: Trigger Scope Reset on destructive Loads (GET DATA / GET FILE)
            if parsed.type == TokenType.FILE_READ:
                # If we have processed nodes, this is a "Memory Wipe" -> New Cluster
                if self.state._get_current_cluster().node_count > 0:
                    self.state.reset_scope()

            # --- DISPATCH LOGIC ---
            if parsed.type == TokenType.ASSIGNMENT:
                self._handle_assignment(parsed.raw) # Pass raw command string
                
            elif parsed.type == TokenType.CONDITIONAL:
                self._handle_conditional(parsed.raw)
            
            # FILE_MATCH (MATCH FILES) merges data, it does NOT wipe memory.
            elif parsed.type == TokenType.FILE_MATCH:
                self._handle_file_match(parsed.raw)

            # FILE_READ (GET DATA) is just a registration now
            elif parsed.type == TokenType.FILE_READ:
                 target = self.extractor.extract_file_target(parsed.raw)
                 if target:
                     self.state.register_input_file(target)

            elif parsed.type == TokenType.FILE_SAVE:
                self._handle_file_save(parsed.raw)
                
            elif parsed.type == TokenType.CONTROL_FLOW:
                self._handle_control_flow(parsed.raw)
                
            elif parsed.type == TokenType.AGGREGATE:
                self._handle_aggregate(parsed.raw)

            elif parsed.type == TokenType.RECODE:
                # Treat Recode as assignment
                self._handle_assignment(parsed.raw)

    # --- HANDLERS (Updated to use self.state) ---

    def _handle_assignment(self, command: str):
        target_var = self.extractor.extract_target(command)
        if target_var:
            raw_deps = self.extractor.extract_dependencies(command)
            resolved_deps = []
            for dep_name in raw_deps:
                if dep_name.upper() == target_var.upper(): continue 
                try:
                    current_ver = self.state.get_current_version(dep_name)
                    resolved_deps.append(current_ver)
                except ValueError: pass

            self.state.register_assignment(
                var_name=target_var, 
                source=command,
                dependencies=resolved_deps
            )

    def _handle_conditional(self, command: str):
        self.state.register_conditional(command)
        target = self.extractor.extract_target(command)
        if target: self._handle_assignment(command)

    def _handle_file_match(self, command: str):
        cmd_upper = command.strip().upper()
        
        pattern = r"/(?:TABLE|FILE)\s*=\s*(?:['\"]([^'\"]+)['\"]|([^\s/]+))"
        matches = re.findall(pattern, command, re.IGNORECASE)
        
        for quoted, unquoted in matches:
            filename = quoted if quoted else unquoted
            if filename != "*":
                self.state.register_input_file(filename)
        
        if "/FILE=*" not in cmd_upper:
             self.state.reset_scope()

        self.join_counter += 1
        sys_id = f"###SYS_JOIN_{self.join_counter}###"
        self.state.register_assignment(
            var_name=sys_id, 
            source=command, 
            dependencies=[]
        )

    def _handle_control_flow(self, command: str):
        self.state.register_control_flow(command)
        # Note: FILE_READ handled in main loop now, but we keep this for legacy safety
        cmd_upper = command.strip().upper()
        
        if cmd_upper.startswith("GET DATA"):
             # Logic moved to main loop, but regex extraction remains useful
             pass

    def _handle_file_save(self, command: str):
        self.state.register_control_flow(command)
        
        pattern = r"/?OUTFILE\s*=\s*(?:['\"]([^'\"]+)['\"]|([^\s/]+))"
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            filename = match.group(1) if match.group(1) else match.group(2)
            self.state.register_output_file(filename)

    def _handle_aggregate(self, command: str):
        matches = re.findall(r"/\s*([A-Za-z0-9_]+)\s*=", command)
        break_match = re.search(r"/BREAK\s*=\s*([A-Za-z0-9_\s]+)", command, re.IGNORECASE)
        deps = []
        if break_match:
            break_vars = break_match.group(1).split()
            for bv in break_vars:
                try:
                    deps.append(self.state.get_current_version(bv))
                except ValueError: pass

        for target in matches:
            if target.upper() not in ["OUTFILE", "BREAK", "PRESORTED", "DOCUMENT", "MISSING"]:
                self.state.register_assignment(
                    var_name=target, 
                    source=command, 
                    dependencies=deps
                )
        
        pattern = r"/OUTFILE\s*=\s*(?:['\"]([^'\"]+)['\"]|([^\s/]+))"
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            filename = match.group(1) if match.group(1) else match.group(2)
            if filename != "*":
                self.state.register_output_file(filename)

    # --- Utilities ---

    def analyze_dead_code(self) -> List[str]:
        raw_dead_ids = self.state.find_dead_versions()
        return [vid for vid in raw_dead_ids if "###SYS_" not in vid]

    def process_file(self, file_path: str):
        if not os.path.exists(file_path): raise FileNotFoundError(f"Source file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f: self.process(f.read())

    def get_variable_version(self, var_name: str) -> Optional[VariableVersion]:
        history = self.state.get_history(var_name)
        if history: return history[-1]
        return None

    def get_variable_history(self, var_name: str):
        return self.state.get_history(var_name)
"""        



I will treat this as a serious submission for an academic–industrial hybrid role. The code shows clear competence and domain insight, but it also reveals architectural immaturity that would concern me for a long-lived research or production system.

I will structure this as:

1. Overall impression
2. Strengths
3. Major architectural concerns
4. Design/code quality issues
5. What I would expect the candidate to improve

---

## 1. Overall impression

This is **not novice code**. The candidate clearly understands:

* SPSS semantics (FILE READ vs MATCH FILES, destructive loads, etc.)
* Program analysis concepts (state, versions, dependencies, dead code)
* The need for lexical, syntactic, and semantic phases

However, the implementation is **procedural orchestration disguised as an object-oriented pipeline**. The file mixes *parsing*, *semantic analysis*, *execution semantics*, and *state mutation* in a way that will **not scale**, either conceptually or in team settings.

This is the work of a **strong individual contributor**, not yet of an architect.

---

## 2. Strengths (these matter)

### a) Correct semantic instincts

The distinction between:

* `FILE_READ` wiping memory
* `FILE_MATCH` merging
* `AGGREGATE` creating derived variables with BREAK dependencies

is non-trivial. Many engineers would get this wrong. You did not.

That tells me you understand the *language*, not just Python.

### b) Explicit state modelling

Using `StateMachine` and `VariableVersion` instead of raw dicts is a very good decision. It shows you are thinking in terms of *semantic history*, not values.

### c) Pipeline intent is clear

Even though the implementation is messy, the *intent* is readable:

```
Lex → Parse → Dispatch → State mutation → Analysis
```

That matters in academic software.

---

## 3. Major architectural concerns (this is where I am strict)

### ❌ 1. The class violates **Single Responsibility** badly

`CompilerPipeline` currently does **all of the following**:

* Orchestrates compiler phases
* Implements semantic rules
* Decides cluster boundaries
* Mutates global analysis state
* Performs regex-based parsing
* Implements dead-code filtering logic

This is not a pipeline. This is a **god object**.

From an architectural perspective, I would expect **at least**:

* A `PipelineCoordinator`
* A `SemanticAnalyzer`
* A `FileEffectAnalyzer`
* A `VariableDependencyResolver`

Right now, everything is entangled.

> If I asked you to add a second backend (e.g. SQL or R IR), this design would collapse.

---

### ❌ 2. Hidden coupling via `parsed.type`

The dispatch logic:

```python
if parsed.type == TokenType.ASSIGNMENT:
    ...
elif parsed.type == TokenType.CONDITIONAL:
    ...
```

means:

* The pipeline must understand *every semantic category*
* Adding a new token type requires editing this class

This is **closed for extension, open for modification** — the opposite of what you want.

Architecturally, this should be:

* A registry of handlers
* Or a visitor over an AST
* Or double dispatch (`parsed.handle(self)`)

Right now, this is a switch statement in disguise.

---

### ❌ 3. Regex-based semantics inside the pipeline

Examples:

```python
pattern = r"/(?:TABLE|FILE)\s*=\s*..."
re.findall(pattern, command)
```

and:

```python
matches = re.findall(r"/\s*([A-Za-z0-9_]+)\s*=", command)
```

This is **semantic analysis by regex**, which is brittle and intellectually inconsistent with having a lexer and parser.

From an architectural standpoint:

* Either trust your parser and extract structured data
* Or admit you don’t have a real parser yet

Mixing both is a design smell.

---

### ❌ 4. Use of private state internals

This line is a red flag:

```python
if self.state._get_current_cluster().node_count > 0:
```

You are reaching *into* the internals of `StateMachine`.

This violates encapsulation and tells me the state abstraction is **leaking**.

As an architect, I would ask:

> Why does the pipeline know clusters exist at all?

The state should expose **intent-based queries**, e.g.:

```python
if self.state.has_semantic_content():
```

---

### ❌ 5. Backward-compatibility aliasing

```python
self.state_machine = self.state  # Alias for backward compatibility
```

This is technical debt embedded directly into the constructor.

In an academic or long-term research codebase, this is unacceptable without a clear deprecation strategy.

At minimum, this should be:

* Isolated
* Documented
* Temporary

Here it looks permanent.

---

## 4. Code quality & design issues

### a) Silent exception swallowing

```python
try:
    current_ver = self.state.get_current_version(dep_name)
except ValueError:
    pass
```

This hides semantic errors and makes correctness unverifiable.

As a professor, I would ask:

> Is missing dependency information acceptable, or is this a bug?

Right now, the code does not know.

---

### b) Magic strings and sentinel values

```python
sys_id = f"###SYS_JOIN_{self.join_counter}###"
```

and later:

```python
if "###SYS_" not in vid
```

This is fragile and not type-safe.

Architecturally, system variables should be **typed**, not string-encoded.

---

### c) Method granularity is inconsistent

Some handlers are trivial pass-throughs:

```python
def _handle_control_flow(self, command: str):
    self.state.register_control_flow(command)
```

Others do heavy semantic work.

This suggests the abstraction boundary is wrong: handlers are not cohesive units.

---

### d) Lack of explicit intermediate representation (IR)

You jump from:

```
raw command → immediate state mutation
```

There is no stable IR layer.

From a research and tooling perspective, this is a serious limitation. You cannot:

* Re-run analysis
* Serialize semantics
* Swap backends
* Test semantic rules independently

---

## 5. What I would expect the candidate to do next

If this were a hiring decision, I would say:

> **Strong hire only if the candidate can refactor this.**

Specifically, I would expect the following improvements:

### 1. Introduce a Semantic IR

Commands should be transformed into structured semantic events:

* `AssignmentEvent`
* `FileReadEvent`
* `JoinEvent`
* `AggregateEvent`

The pipeline should *emit* these, not act on them.

---

### 2. Move state mutation out of the pipeline

The pipeline should coordinate, not decide semantics.

A proper architecture would be:

```
Lexer → Parser → AST → Semantic Events → State Analyzer
```

---

### 3. Replace regex semantics with parser output

If the parser cannot provide this information yet, improve the parser — do not patch around it.

---

### 4. Make `StateMachine` a real abstraction

No private access. No magic strings. Clear intent-based methods.

---

### 5. Formalise extension points

Adding a new SPSS command type should not require editing this file.

---

## Final verdict

* **Technical ability:** High
* **Domain understanding:** Very high
* **Architectural maturity:** Medium
* **Maintainability as-is:** Low
* **Potential:** Excellent

This code convinces me you can *solve hard problems*. It does **not yet convince me** you can *design systems that other people can safely extend*.

That is the difference between a strong developer and an associate professor.
