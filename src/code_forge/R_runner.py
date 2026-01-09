import os
import csv
import subprocess
import logging
import pandas as pd
from typing import Dict, Optional, List, Set
from spss_engine.state import StateMachine

logger = logging.getLogger("RRunner")

class RRunner:
    """
    Executes the generated R code to verify it produces the same numbers as SPSS.
    """
    def __init__(self, r_script_path: str, state_machine: Optional[StateMachine] = None):
        self.script_path = os.path.abspath(r_script_path)
        self.work_dir = os.path.dirname(self.script_path)
        self.state_machine = state_machine
        
    def _discover_inputs(self) -> List[str]:
        """
        Scans the State Machine to find variables that are USED but not DEFINED.
        """
        if not self.state_machine:
            logger.debug("⚠️ No StateMachine provided for input discovery.")
            return []
            
        # 1. Gather all variables defined in this script (The "Nodes")
        # We assume node names are UPPERCASE in the backend
        defined_vars = {node.name.upper() for node in self.state_machine.nodes}
        
        # 2. Gather all variables required by those nodes (The "Dependencies")
        required_vars = set()
        
        for node in self.state_machine.nodes:
            for dep in node.dependencies:
                # Handle both object and potentially string legacy refs
                d_name = dep.name if hasattr(dep, 'name') else str(dep)
                # Clean up name (remove version suffixes if any exist in loose references)
                d_name = d_name.split('_')[0].upper()
                required_vars.add(d_name)

        # 3. Calculate the difference: Required - Defined = Inputs
        missing_vars = list(required_vars - defined_vars)
        
        # 🟢 CRITICAL FIX: Coerce to lowercase.
        # The RGenerator outputs lowercase variables (e.g., 'age', 'income').
        # The dataframe must match this case.
        missing_vars_lower = [v.lower() for v in missing_vars]
        
        logger.debug(f"🔎 Input Discovery:")
        logger.debug(f"   Defined: {defined_vars}")
        logger.debug(f"   Required: {required_vars}")
        logger.debug(f"   Detected Inputs: {missing_vars_lower}")
        
        return missing_vars_lower

    def run_and_capture(self, input_vars: List[str] = None) -> Dict[str, float]:
        wrapper_path = os.path.join(self.work_dir, "run_wrapper.R")
        output_csv = os.path.join(self.work_dir, "r_output.csv")
        
        # 🟢 Auto-discover inputs if not provided
        if input_vars is None:
            input_vars = self._discover_inputs()
        else:
            # Ensure manually passed vars are also lowercase
            input_vars = [v.lower() for v in input_vars]

        # Initialize dummy columns (Default to 1 to avoid DivisionByZero/NA errors)
        cols_init = ""
        if input_vars:
            cols = [f'{var} = 1' for var in input_vars] 
            cols_init = ", ".join(cols)
        
        # Always provide a fallback ID
        if not cols_init:
            cols_init = "id = 1"
        else:
            cols_init += ", id = 1"
            
        r_wrapper = f"""
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)

        source("{os.path.basename(self.script_path)}")
        
        # Create dummy DF with discovered inputs
        df <- data.frame({cols_init})
        
        # Run safely
        tryCatch({{
            result <- logic_pipeline(df)
            write.csv(result, "{output_csv}", row.names = FALSE)
        }}, error = function(e) {{
            message("CRITICAL R ERROR: ", e$message)
            quit(status = 1)
        }})
        """
        
        with open(wrapper_path, "w") as f:
            f.write(r_wrapper)
            
        try:
            # Run Rscript. We use capture_output=True to keep stdout clean unless verbose
            subprocess.run(
                ["Rscript", wrapper_path], 
                check=True, 
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            # Only log error if it actually failed
            logger.error(f"R Execution Failed:\n{e.stderr}")
            return {}
            
        if not os.path.exists(output_csv):
            return {}
            
        return self._read_first_row(output_csv)

    def _read_first_row(self, csv_path: str) -> Dict[str, float]:
        results = {}
        try:
            df = pd.read_csv(csv_path)
            if not df.empty:
                row = df.iloc[-1]
                for col in df.columns:
                    key = col.upper() 
                    try:
                        val = float(row[col])
                        results[key] = val
                    except (ValueError, TypeError):
                        pass 
        except Exception as e:
            logger.error(f"Failed to read R output: {e}")
            
        return results