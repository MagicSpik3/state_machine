#src/code_forge/generator.py
import logging
import re
from typing import List, Optional
from spss_engine.state import StateMachine, VariableVersion, InputSchema
from spss_engine.events import FileReadEvent, SemanticEvent

logger = logging.getLogger("RGenerator")

class RGenerator:
    def __init__(self, state_machine: StateMachine):
        self.state = state_machine
        self.script_lines: List[str] = []

    def generate_script(self, lookups: List[str] = None) -> str:
        self.script_lines = []
        self._add_header()
        
        if self.state and not self.state.nodes:
             self.script_lines.append("# No logic detected.")
             return "\n".join(self.script_lines)

        # Clean Lookup List
        lookup_args = []
        if lookups:
            for f in lookups:
                arg = f.split('.')[0]
                lookup_args.append(arg)
        lookup_args = sorted(list(set(lookup_args)))

        # Generate Function Signature
        self.script_lines.append("#' Logic Pipeline")
        self.script_lines.append("#' @param df Main dataframe")
        for arg in lookup_args:
             self.script_lines.append(f"#' @param {arg} Lookup table (Optional)")
        self.script_lines.append("#' @export")
        
        sig_args = ["df"] + [f"{arg} = NULL" for arg in lookup_args]
        self.script_lines.append(f"logic_pipeline <- function({', '.join(sig_args)}) {{")
        
        # 🟢 NEW: Type Enforcement based on Schema (Contract Fulfillment)
        if self.state.inputs:
            self.script_lines.append("  # --- Schema Type Enforcement ---")
            for schema in self.state.inputs:
                # We assume the main dataframe 'df' matches the first registered schema
                # or generically apply to 'df' if names match
                self._generate_type_enforcement(schema, "df")
            self.script_lines.append("  # -------------------------------")

        self.script_lines.append("  df <- df %>%") 
        
        # Generate Body
        active_nodes = list(self.state.nodes) if self.state else [] # Safety copy
        for i, node in enumerate(active_nodes):
            r_code = self._transpile_node(node)
            if r_code:
                self.script_lines.append(f"    {r_code} %>%")

        if self.script_lines[-1].strip().endswith("%>%"):
             self.script_lines[-1] = self.script_lines[-1].rstrip(" %>%")

        self.script_lines.append("  return(df)")
        self.script_lines.append("}")
        
        return "\n".join(self.script_lines)

    def _generate_type_enforcement(self, schema: InputSchema, df_name: str):
        """
        Generates R code to cast columns to their schema-defined types.
        """
        for col in schema.columns:
            r_col = f"{df_name}${col.name}"
            if col.type_generic == "Numeric":
                self.script_lines.append(f"  {r_col} <- as.numeric({r_col})")
            elif col.type_generic == "String":
                self.script_lines.append(f"  {r_col} <- as.character({r_col})")
            elif col.type_generic == "Date":
                # Default SPSS format assumption, can be refined later
                self.script_lines.append(f"  {r_col} <- as.Date({r_col}, format='%d-%b-%Y')")

    def generate_loader_snippet(self, event: FileReadEvent) -> str:
        """
        Public method to generate just the data loading block.
        Used by RRunner to ensure test execution matches production logic.
        """
        # 🟢 CHANGED: Try to find the Schema first
        found_schema = None
        if self.state.inputs:
            for s in self.state.inputs:
                if s.filename == event.filename:
                    found_schema = s
                    break
        
        # Temporarily hijack self.script_lines
        original_lines = self.script_lines
        self.script_lines = []
        
        if found_schema:
            self._generate_loader_from_schema(found_schema)
        else:
            # Fallback to event-based (Legacy)
            self._generate_loader_block(event)
        
        snippet = "\n".join(self.script_lines)
        self.script_lines = original_lines
        return snippet


# ... inside RGenerator class ...

    def _generate_loader_from_schema(self, schema: InputSchema):
        """Generates read code from the Schema object."""
        var_name = "df"
        if schema.format == "SAV":
            self.script_lines.append(f"{var_name} <- read_sav('{schema.filename}')")
        else:
            safe_delim = schema.delimiter.replace('"', '\\"') if schema.delimiter else ","
            self.script_lines.append(f"{var_name} <- read.csv(")
            self.script_lines.append(f"  file = '{schema.filename}',")
            self.script_lines.append(f"  sep = '{safe_delim}',")
            self.script_lines.append(f"  stringsAsFactors = FALSE")
            self.script_lines.append(f")")
            
        # 🟢 FIX: Call the type enforcement logic here too!
        # This ensures the RRunner (and tests) get the types, not just the main script.
        if schema.columns:
            self.script_lines.append("")
            self.script_lines.append("# Enforce Schema Types")
            self._generate_type_enforcement(schema, var_name)




    def _transpile_node(self, node: VariableVersion) -> str:
        if not hasattr(node, 'source'):
             return f"# Error: Node {node.name} missing source code"
        
        expr = node.source.strip()
        target = node.name.lower()
        
        if expr.upper().startswith("COMPUTE"):
            parts = expr.split("=", 1)
            if len(parts) == 2:
                rhs = parts[1].strip().rstrip(".").lower()
                return f"mutate({target} = {rhs})"

        elif expr.upper().startswith("IF"):
            match = re.search(r"IF\s*\((.*?)\)\s*(\w+)\s*=\s*(.*)\.$", expr, re.IGNORECASE)
            if match:
                condition = match.group(1).lower()
                value_true = match.group(3).lower()
                return f"mutate({target} = if_else({condition}, {value_true}, {target}))"

        # 🟢 RESTORED JOIN LOGIC
        elif "MATCH FILES" in expr.upper():
             # MATCH FILES /TABLE='lookup.sav' /BY id.
             # Naive extraction for Left Join
             table_match = re.search(r"/TABLE\s*=\s*['\"](.*?)['\"]", expr, re.IGNORECASE)
             by_match = re.search(r"/BY\s+(\w+)", expr, re.IGNORECASE)
             
             if table_match and by_match:
                 table_file = table_match.group(1)
                 # Assumption: Argument name matches filename base (lookup.sav -> lookup)
                 table_arg = table_file.split('.')[0]
                 key = by_match.group(1).lower()
                 return f"left_join({table_arg}, by='{key}')"
             
             return f"# Complex Join detected: {expr}"
        
        return f"# Unhandled logic: {expr}"

    def generate_standalone_script(self, events: List[SemanticEvent]) -> str:
        # Legacy support
        self.script_lines = []
        self.script_lines.append("library(dplyr)")
        self.script_lines.append("library(readr)")
        self.script_lines.append("")
        for event in events:
            if isinstance(event, FileReadEvent):
                self._generate_loader_block(event)
        return "\n".join(self.script_lines)

    def _generate_loader_block(self, event: FileReadEvent):
        # Legacy fallback
        raw_delim = event.delimiter if event.delimiter else ","
        raw_qual = event.qualifier if event.qualifier else '"'
        safe_delim = raw_delim.replace('"', '\\"')
        safe_qual = raw_qual.replace('"', '\\"')
        header_bool = "TRUE" if event.header_row else "FALSE"
        filename = event.filename if event.filename else "unknown.csv"
        
        self.script_lines.append(f"# Load Data: {filename}")
        self.script_lines.append(f"df <- read.csv(")
        self.script_lines.append(f'  file = "{filename}",')
        self.script_lines.append(f"  header = {header_bool},")
        self.script_lines.append(f'  sep = "{safe_delim}",')
        self.script_lines.append(f'  quote = "{safe_qual}",')
        self.script_lines.append(f"  stringsAsFactors = FALSE")
        self.script_lines.append(f")")
        self.script_lines.append("")

    def generate_description(self, pkg_name: str) -> str:
        return f"""Package: {pkg_name}
Title: Converted SPSS Logic
Version: 0.1.0
Description: Auto-generated from SPSS source.
Imports: dplyr, readr, lubridate
Encoding: UTF-8
RoxygenNote: 7.2.3
"""
    
    def _add_header(self):
        self.script_lines.append("# Auto-generated R script")
        self.script_lines.append("library(dplyr)")
        self.script_lines.append("library(readr)")
        self.script_lines.append("library(lubridate)")
        self.script_lines.append("")