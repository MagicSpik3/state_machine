import re
from typing import List, Set, Dict
from spss_engine.state import StateMachine, VariableVersion

class RGenerator:
    """
    Converts a verified StateMachine into a production-ready R script (Tidyverse).
    """
    def __init__(self, state_machine: StateMachine):
        self.state = state_machine
        self.contract_inputs: Set[str] = set()

    def generate_description(self, package_name: str) -> str:
        """Generates the content for the R package DESCRIPTION file."""
        lines = [
            f"Package: {package_name}",
            "Title: Converted Legacy Logic",
            "Version: 0.1.0",
            "Authors@R: person('Statify', 'Bot', email='bot@example.com', role = c('aut', 'cre'))",
            "Description: Auto-generated logic pipeline derived from legacy SPSS source code.",
            "Imports:",
            "    dplyr,",
            "    readr,",
            "    lubridate",
            "Encoding: UTF-8",
            "LazyData: true",
            "RoxygenNote: 7.2.3"
        ]
        return "\n".join(lines)

    def generate_script(self) -> str:
        execution_order = self._topological_sort()
        self._analyze_contract(execution_order)
        
        lines = []
        lines.append("library(dplyr)")
        lines.append("library(readr)")
        lines.append("library(lubridate)")
        lines.append("")
        lines.append("")
        lines.append("#' Logic Pipeline")
        lines.append("#' @description Auto-generated logic derived from legacy SPSS.")
        lines.append("#' @section Data Contract:")
        lines.append("#' Required Input Columns:")
        
        sorted_inputs = sorted(list(self.contract_inputs))
        if not sorted_inputs:
            lines.append("#'  (None detected - Self-contained logic)")
        else:
            for inp in sorted_inputs:
                lines.append(f"#'  - {inp}")
            
        lines.append("#' @export")
        lines.append("logic_pipeline <- function(df) {")
        lines.append("  df <- df %>%")
        
        for i, node in enumerate(execution_order):
            r_code = self._transpile_node(node)
            if r_code:
                separator = " %>%" if i < len(execution_order) - 1 else ""
                lines.append(f"    {r_code}{separator}")
                
        lines.append("  return(df)")
        lines.append("}")
        return "\n".join(lines)

    def _analyze_contract(self, nodes: List[VariableVersion]):
        created_vars = set()
        for node in nodes:
            var_name = node.id.rsplit('_', 1)[0]
            created_vars.add(var_name)
            for dep_id in node.dependencies:
                dep_name = dep_id.rsplit('_', 1)[0]
                if dep_name not in created_vars:
                    # Ignore self-references
                    if dep_name != var_name:
                        self.contract_inputs.add(dep_name)

    def _topological_sort(self) -> List[VariableVersion]:
        all_nodes = []
        for history in self.state.history_ledger.values():
            all_nodes.extend(history)
        return all_nodes


    def _transpile_node(self, node: VariableVersion) -> str:
        # 1. Target: Lowercase (snake_case)
        target = node.id.rsplit('_', 1)[0].lower() 
        source = node.source.strip()
        
        def normalize_rhs(expression: str) -> str:
            # Replace dependencies with their lowercase equivalents
            for dep_id in node.dependencies:
                dep_name = dep_id.rsplit('_', 1)[0]
                # Regex to match the dependency name case-insensitively and replace with lowercase
                expression = re.sub(
                    rf"(?i)\b{dep_name}\b", 
                    dep_name.lower(), 
                    expression
                )
            return expression


        # 1. COMPUTE
        if re.match(r"(?i)^COMPUTE", source):
            if "=" in source:
                rhs = source.split("=", 1)[1].strip().rstrip(".")
                rhs = normalize_rhs(rhs) # <--- APPLY FIX
                return f"mutate({target} = {rhs})"

        # 2. IF (Conditional)
        if re.match(r"(?i)^IF", source):
            match = re.search(r"(?i)IF\s*\((.+)\)\s+(\w+)\s*=\s*(.+?)\.?$", source)
            if match:
                condition = normalize_rhs(match.group(1).strip()) # Fix casing in condition
                # target is implicit
                value = normalize_rhs(match.group(3).strip())     # Fix casing in value
                return f"mutate({target} = if_else({condition}, {value}, {target}))"

        return f"# TODO: Port {source}"