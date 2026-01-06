import re
from typing import List, Set, Dict
from spss_engine.state import StateMachine, VariableVersion
from code_forge.rosetta import RosettaStone

class RGenerator:
    def __init__(self, state_machine: StateMachine):
        self.state = state_machine
        self.contract_inputs: Set[str] = set()
        self.processed_joins: Set[str] = set()

    def generate_description(self, package_name: str) -> str:
        return f"Package: {package_name}\nTitle: Auto-Generated Logic\nVersion: 0.1.0\nImports: dplyr, readr, lubridate"

    def _get_join_blocks(self) -> List[str]:
        """
        Scans the entire state for MATCH FILES commands and generates left_join logic.
        This runs BEFORE the variable calculation loop.
        """
        joins = []
        # Scan every single line of code we parsed
        all_versions = [v for hist in self.state.history_ledger.values() for v in hist]
        
        # Sort by source position to maintain order (roughly)
        # In a real engine, we'd use line numbers. Here we rely on list order.
        
        seen_tables = set()
        
        for version in all_versions:
            source = version.source.strip().upper()
            if source.startswith("MATCH FILES"):
                # Regex for /TABLE='file' and /BY key
                table_match = re.search(r"/TABLE=['\"]([^'\"]+)['\"]", source)
                by_match = re.search(r"/BY\s+(\w+)", source)
                
                if table_match and by_match:
                    full_filename = table_match.group(1) # e.g. 'benefit_rates.sav'
                    key = by_match.group(1).lower()
                    
                    # Clean Table Name
                    table_name = full_filename.split('.')[0].lower() # 'benefit_rates'
                    table_name = re.sub(r'[^a-z0-9_]', '', table_name)
                    
                    if table_name not in seen_tables:
                        seen_tables.add(table_name)
                        # Generate the Join
                        joins.append(f"left_join({table_name}, by='{key}')")
                        
        return joins

    def generate_script(self) -> str:
        execution_order = self._topological_sort()
        
        # 1. Identify Tables needed
        join_ops = self._get_join_blocks()
        
        # Extract table names from the join ops for the function signature
        # e.g. "left_join(benefit_rates, ...)" -> "benefit_rates"
        external_tables = []
        for j in join_ops:
            m = re.search(r"left_join\(([^,]+)", j)
            if m: external_tables.append(m.group(1))
        
        lines = []
        lines.append("library(dplyr)")
        lines.append("library(readr)")
        lines.append("library(lubridate)")
        lines.append("")
        
        # 2. Function Signature
        args = ["df"] + [f"{tbl} = NULL" for tbl in external_tables]
        sig = ", ".join(args)
        
        lines.append("#' Logic Pipeline")
        lines.append(f"#' @param df Main dataframe")
        for tbl in external_tables:
            lines.append(f"#' @param {tbl} Reference table (Auto-detected)")
        lines.append("#' @export")
        lines.append(f"logic_pipeline <- function({sig}) {{")
        
        # 3. Data Loading Fallback (CRITICAL FIX)
        if external_tables:
            lines.append("  # --- Auto-Load Missing Dependencies ---")
            for tbl in external_tables:
                # Fallback to CSV if object is missing
                lines.append(f"  if(is.null({tbl}) && file.exists(paste0('{tbl}.csv'))) {{")
                lines.append(f"    {tbl} <- read_csv(paste0('{tbl}.csv'), show_col_types = FALSE)")
                lines.append(f"  }}")
            lines.append("")

        lines.append("  df <- df %>%")
        
        # 4. Inject Joins FIRST (Phase A)
        for join_cmd in join_ops:
            lines.append(f"    {join_cmd} %>%")

        # 5. Inject Calculations (Phase B)
        for i, node in enumerate(execution_order):
            # Skip MATCH FILES here since we handled them in Phase A
            if node.source.upper().startswith("MATCH FILES"):
                continue
                
            r_code = self._transpile_node(node)
            if r_code:
                lines.append(f"    {r_code} %>%")

        # Cleanup trailing pipe
        if lines[-1].strip().endswith("%>%"):
             lines[-1] = lines[-1].rsplit("%>%", 1)[0]

        lines.append("  return(df)")
        lines.append("}")
        return "\n".join(lines)

    def _transpile_node(self, node: VariableVersion) -> str:
        # Simplified transpiler (Removed Join logic as it moved to _get_join_blocks)
        target = node.id.rsplit('_', 1)[0].lower()
        source = node.source.strip()
        
        def normalize_rhs(expression: str) -> str:
            for dep_id in node.dependencies:
                dep_name = dep_id.rsplit('_', 1)[0]
                expression = re.sub(rf"(?i)\b{dep_name}\b", dep_name.lower(), expression)
            return RosettaStone.translate_expression(expression)

        if re.match(r"(?i)^COMPUTE", source):
            if "=" in source:
                rhs = source.split("=", 1)[1].strip().rstrip(".")
                rhs = normalize_rhs(rhs)
                return f"mutate({target} = {rhs})"

        if re.match(r"(?i)^IF", source):
            match = re.search(r"(?i)IF\s*\((.+)\)\s+(\w+)\s*=\s*(.+?)\.?$", source)
            if match:
                condition = normalize_rhs(match.group(1).strip())
                value = normalize_rhs(match.group(3).strip())
                return f"mutate({target} = if_else({condition}, {value}, {target}))"

        if re.match(r"(?i)^STRING", source):
             return f"mutate({target} = as.character(NA))"

        return None
    
    # Keep _topological_sort and _analyze_contract as is
    def _topological_sort(self) -> List[VariableVersion]:
        all_nodes = []
        for history in self.state.history_ledger.values():
            all_nodes.extend(history)
        return all_nodes

    def _analyze_contract(self, nodes: List[VariableVersion]):
        pass