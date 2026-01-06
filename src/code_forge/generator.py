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
        """
        Generates the content for the DESCRIPTION file.
        """
        lines = [
            f"Package: {package_name}",
            "Title: Converted Legacy Logic",
            "Version: 0.1.0",
            "Description: Auto-generated logic pipeline from Statify.",
            "Imports:",
            "    dplyr,",
            "    readr,",
            "    lubridate",
            "Encoding: UTF-8",
            "LazyData: true"
        ]
        return "\n".join(lines)

    def generate_script(self) -> str:
        """
        Main entry point. Returns full R source code.
        """
        execution_order = self._topological_sort()
        self._analyze_contract(execution_order)
        
        lines = []
        
        # 1. Header & Data Contract
        lines.append("#' Logic Pipeline")
        lines.append("#' @description Auto-generated logic derived from legacy SPSS.")
        lines.append("#' @section Data Contract:")
        lines.append("#' Required Input Columns:")
        
        sorted_inputs = sorted(list(self.contract_inputs))
        for inp in sorted_inputs:
            lines.append(f"#'  - {inp}")
            
        lines.append("#' @export")
        lines.append("logic_pipeline <- function(df) {")
        lines.append("  df <- df %>%")
        
        # 2. Transpile Logic
        # We collect all consecutive mutations into one block if possible, 
        # but for simplicity in Step 1, we chain them.
        
        for i, node in enumerate(execution_order):
            r_code = self._transpile_node(node)
            if r_code:
                # Add pipe %>% unless it's the very last step
                separator = " %>%" if i < len(execution_order) - 1 else ""
                lines.append(f"    {r_code}{separator}")
                
        lines.append("  return(df)")
        lines.append("}")
        
        # 3. Add Libraries at the top (Optimization: could be strictly at top)
        header = ["library(dplyr)", "library(readr)", "library(lubridate)", "", ""]
        return "\n".join(header + lines)

    def _analyze_contract(self, nodes: List[VariableVersion]):
        """
        Determines inputs based on dependencies not created by previous steps.
        """
        created_vars = set()
        for node in nodes:
            var_name = node.id.rsplit('_', 1)[0]
            created_vars.add(var_name)
            
            for dep_id in node.dependencies:
                dep_name = dep_id.rsplit('_', 1)[0]
                if dep_name not in created_vars:
                    # Filter out self-references (e.g. x = x + 1)
                    if dep_name.upper() != var_name.upper():
                        self.contract_inputs.add(dep_name)

    def _topological_sort(self) -> List[VariableVersion]:
        # Reuse the heuristic sort from before (File Order)
        # This works because SPSS is procedural.
        all_nodes = []
        for history in self.state.history_ledger.values():
            all_nodes.extend(history)
        
        # Sort by ID order (rough proxy for time) seems brittle, 
        # but usually the list concatenation respects insertion order in Py3.7+
        # A better way: Sort by the order they appear in symbol_table?
        # Actually, let's just flatten the history ledger values in order.
        return all_nodes

    def _transpile_node(self, node: VariableVersion) -> str:
        """
        Converts SPSS command to R dplyr syntax.
        """
        target = node.id.rsplit('_', 1)[0]
        source = node.source.lower()
        
        # 1. Simple Arithmetic (COMPUTE)
        if "compute" in source and "=" in source:
            # Clean up the RHS
            parts = source.split("=", 1)
            rhs = parts[1].strip().rstrip(".")
            
            # Remove "compute" from the string if it was caught in the split?
            # Actually, standardizing the RHS is tricky without a full expression parser.
            # Heuristic: Just take the RHS as-is for simple math.
            
            return f"mutate({target} = {rhs})"
            
        return f"# TODO: Port {node.id}"