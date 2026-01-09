import logging
import re
from typing import List, Optional
from spss_engine.state import StateMachine, VariableVersion
from spss_engine.events import FileReadEvent, SemanticEvent

logger = logging.getLogger("RGenerator")

class RGenerator:
    def __init__(self, state_machine: StateMachine):
        self.state = state_machine
        self.script_lines: List[str] = []

    # 🟢 CHANGED: Accept 'lookups' explicitly. No internal discovery.
    def generate_script(self, lookups: List[str] = None) -> str:
        self.script_lines = []
        self._add_header()
        
        if self.state and not self.state.nodes:
             self.script_lines.append("# No logic detected.")
             return "\n".join(self.script_lines)

        # Clean Lookup List
        lookup_args = []
        if lookups:
            # Convert filenames (lookup.sav) to arg names (lookup)
            # Filter out the main input file if it accidentally got passed here
            for f in lookups:
                arg = f.split('.')[0]
                lookup_args.append(arg)
        
        # Sort for deterministic output
        lookup_args = sorted(list(set(lookup_args)))

        # Generate Function Signature
        self.script_lines.append("#' Logic Pipeline")
        self.script_lines.append("#' @param df Main dataframe")
        for arg in lookup_args:
             self.script_lines.append(f"#' @param {arg} Lookup table (Optional)")
        self.script_lines.append("#' @export")
        
        sig_args = ["df"] + [f"{arg} = NULL" for arg in lookup_args]
        self.script_lines.append(f"logic_pipeline <- function({', '.join(sig_args)}) {{")
        self.script_lines.append("  df <- df %>%") 
        
        # Generate Body
        active_nodes = self.state.nodes
        for i, node in enumerate(active_nodes):
            r_code = self._transpile_node(node)
            if r_code:
                self.script_lines.append(f"    {r_code} %>%")

        if self.script_lines[-1].strip().endswith("%>%"):
             self.script_lines[-1] = self.script_lines[-1].rstrip(" %>%")

        self.script_lines.append("  return(df)")
        self.script_lines.append("}")
        
        return "\n".join(self.script_lines)

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

        elif "MATCH FILES" in expr.upper():
             return f"# Join logic detected: {expr}"
        
        return f"# Unhandled logic: {expr}"

    # ... (Rest of file: generate_standalone_script, etc. remains unchanged) ...
    def generate_standalone_script(self, events: List[SemanticEvent]) -> str:
        self.script_lines = []
        self.script_lines.append("library(dplyr)")
        self.script_lines.append("library(readr)")
        self.script_lines.append("")
        for event in events:
            if isinstance(event, FileReadEvent):
                self._generate_loader_block(event)
        return "\n".join(self.script_lines)

    def _generate_loader_block(self, event: FileReadEvent):
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

        if event.variables:
            self.script_lines.append(f"# SPSS data types identified and transported to R")
            for var_name, spss_type in event.variables:
                r_col = f"df${var_name}"
                if spss_type.startswith("F") or spss_type.startswith("COMMA") or spss_type.startswith("DOLLAR"):
                    self.script_lines.append(f"{r_col} <- as.numeric({r_col})      # {spss_type}")
                elif spss_type.startswith("A"):
                    self.script_lines.append(f"{r_col} <- as.character({r_col})    # {spss_type}")
                elif "DATE" in spss_type:
                    self.script_lines.append(f"{r_col} <- as.Date({r_col}, format='%d-%b-%Y') # {spss_type}")
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