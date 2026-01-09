import re
from typing import List, Set
from spss_engine.state import StateMachine, VariableVersion
from code_forge.rosetta import RosettaStone

class RGenerator:
    def __init__(self, state_machine: StateMachine):
        self.state = state_machine
        self.processed_joins: Set[str] = set()

    def generate_description(self, package_name: str) -> str:
        # Added haven to imports
        return f"Package: {package_name}\nTitle: Auto-Generated Logic\nVersion: 0.1.0\nImports: dplyr, readr, lubridate, haven"

    def _get_join_blocks(self) -> List[str]:
        """
        Scans the State Machine History for MATCH FILES nodes.
        """
        joins = []
        all_nodes = [node for history in self.state.history_ledger.values() for node in history]
        seen_tables = set()
        
        for node in all_nodes:
            source = node.source.strip().upper()
            if source.startswith("MATCH FILES"):
                # Regex for /TABLE='file' and /BY key
                pattern = re.compile(r"MATCH FILES.*?/TABLE=['\"]([^'\"]+)['\"].*?/BY\s+(\w+)", re.IGNORECASE | re.DOTALL)
                match = pattern.search(source)
                
                if match:
                    filename = match.group(1)
                    key = match.group(2)
                    
                    # Clean Table Name: 'benefit_rates.sav' -> 'benefit_rates'
                    table_name = filename.split('.')[0].lower()
                    table_name = re.sub(r'[^a-z0-9_]', '', table_name)
                    
                    if table_name not in seen_tables:
                        seen_tables.add(table_name)
                        joins.append(f"left_join({table_name}, by='{key.lower()}')")
                        
        return joins

    def generate_script(self) -> str:
        execution_order = self._topological_sort()
        join_ops = self._get_join_blocks()
        
        external_tables = []
        for j in join_ops:
            m = re.search(r"left_join\(([^,]+)", j)
            if m: external_tables.append(m.group(1))
        
        lines = []
        lines.append("library(dplyr)")
        lines.append("library(readr)")
        lines.append("library(lubridate)")
        lines.append("library(haven)") # <--- NEW: Support for SPSS files
        lines.append("")
        
        # Signature
        args = ["df"] + [f"{tbl} = NULL" for tbl in external_tables]
        sig = ", ".join(args)
        
        lines.append("#' Logic Pipeline")
        lines.append(f"#' @param df Main dataframe")
        for tbl in external_tables:
            lines.append(f"#' @param {tbl} Reference table (Auto-detected)")
        lines.append("#' @export")
        lines.append(f"logic_pipeline <- function({sig}) {{")
        
        # Auto-Load Logic (Updated for SAV support)
        if external_tables:
            lines.append("  # --- Auto-Load Missing Dependencies ---")
            for tbl in external_tables:
                # 1. Try CSV
                lines.append(f"  if(is.null({tbl}) && file.exists(paste0('{tbl}.csv'))) {{")
                lines.append(f"    {tbl} <- read_csv(paste0('{tbl}.csv'), show_col_types = FALSE)")
                # 2. Try SAV (SPSS)
                lines.append(f"  }} else if(is.null({tbl}) && file.exists(paste0('{tbl}.sav'))) {{")
                lines.append(f"    {tbl} <- read_sav(paste0('{tbl}.sav'))")
                lines.append(f"  }}")
            lines.append("")

        lines.append("  df <- df %>%")
        
        # Phase A: Joins
        for join_cmd in join_ops:
            lines.append(f"    {join_cmd} %>%")

        # Phase B: Calculations
        for i, node in enumerate(execution_order):
            if node.source.upper().startswith("MATCH FILES"):
                continue
            r_code = self._transpile_node(node)
            if r_code:
                lines.append(f"    {r_code} %>%")

        if lines[-1].strip().endswith("%>%"):
             lines[-1] = lines[-1].rsplit("%>%", 1)[0]

        lines.append("  return(df)")
        lines.append("}")
        return "\n".join(lines)
    

    def _transpile_node(self, node: VariableVersion) -> str:
        target = node.id.rsplit('_', 1)[0].lower()
        source = node.source.strip()
        
        # 🟢 Helper: Normalize variables using the Object, not string splitting
        def normalize_rhs(expression: str) -> str:
            for dep_obj in node.dependencies:
                # FIX: Access .id explicitly because dep_obj is a VariableVersion
                dep_name = dep_obj.id.rsplit('_', 1)[0]
                expression = re.sub(rf"(?i)\b{dep_name}\b", dep_name.lower(), expression)
            return RosettaStone.translate_expression(expression)

        # 1. COMPUTE
        if re.match(r"(?i)^COMPUTE", source):
            if "=" in source:
                rhs = source.split("=", 1)[1].strip().rstrip(".")
                rhs = normalize_rhs(rhs)
                return f"mutate({target} = {rhs})"

        # 2. IF
        if re.match(r"(?i)^IF", source):
            match = re.search(r"(?i)IF\s*\((.+)\)\s+(\w+)\s*=\s*(.+?)\.?$", source)
            if match:
                condition = normalize_rhs(match.group(1).strip())
                value = normalize_rhs(match.group(3).strip())
                return f"mutate({target} = if_else({condition}, {value}, {target}))"

        # 3. RECODE (🟢 NEW LOGIC)
        if re.match(r"(?i)^RECODE", source):
            # Regex to find (old=new) pairs
            pairs = re.findall(r"\(([^=]+)=([^)]+)\)", source)
            
            cases = []
            for old_val, new_val in pairs:
                old_val = normalize_rhs(old_val.strip())
                new_val = normalize_rhs(new_val.strip())
                
                # Handle ELSE
                if old_val.upper() == "ELSE":
                    cases.append(f"TRUE ~ {new_val}")
                else:
                    cases.append(f"{target} == {old_val} ~ {new_val}")
            
            # Default case: Keep original value if no ELSE provided
            if not any("TRUE" in c for c in cases):
                cases.append(f"TRUE ~ {target}")

            args = ", ".join(cases)
            return f"mutate({target} = case_when({args}))"

        # 4. STRING
        if re.match(r"(?i)^STRING", source):
             return f"mutate({target} = as.character(NA))"

        return None


    def _topological_sort(self) -> List[VariableVersion]:
        all_nodes = []
        for history in self.state.history_ledger.values():
            all_nodes.extend(history)
        return all_nodes

    def _analyze_contract(self, nodes: List[VariableVersion]):
        pass


    # ... (Keep _transpile_node, _topological_sort as they were) ...
    def _transpile_node(self, node: VariableVersion) -> str:
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
        
    def _topological_sort(self) -> List[VariableVersion]:
        all_nodes = []
        for history in self.state.history_ledger.values():
            all_nodes.extend(history)
        return all_nodes

    def _analyze_contract(self, nodes: List[VariableVersion]):
        pass