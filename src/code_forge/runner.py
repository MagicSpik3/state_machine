# state_machine/src/code_forge/runner.py
import os
import csv
import subprocess
import logging
import pandas as pd
from typing import Dict, Optional, List

logger = logging.getLogger("RRunner")

class RRunner:
    """
    Executes the generated R code to verify it produces the same numbers as SPSS.
    """
    def __init__(self, r_script_path: str):
        self.script_path = os.path.abspath(r_script_path)
        self.work_dir = os.path.dirname(self.script_path)
        
    def run_and_capture(self, input_vars: List[str] = None) -> Dict[str, float]:
        """
        Runs the R script and returns the final row as a dictionary.
        input_vars: Optional list of columns to initialize in the dummy dataframe.
        """
        wrapper_path = os.path.join(self.work_dir, "run_wrapper.R")
        output_csv = os.path.join(self.work_dir, "r_output.csv")
        
        # Initialize dummy columns
        cols_init = ""
        if input_vars:
            cols = [f'{var} = 0' for var in input_vars] # Initialize as 0 for safety
            cols_init = ", ".join(cols)
        
        if not cols_init:
            cols_init = "id = 1"
            
        r_wrapper = f"""
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)

        source("{os.path.basename(self.script_path)}")
        
        # Create dummy DF
        df <- data.frame({cols_init})
        
        # Run safely
        tryCatch({{
            result <- logic_pipeline(df)
            write.csv(result, "{output_csv}", row.names = FALSE)
        }}, error = function(e) {{
            # Print to stderr so Python catches it
            message("CRITICAL R ERROR: ", e$message)
            quit(status = 1)
        }})
        """
        
        with open(wrapper_path, "w") as f:
            f.write(r_wrapper)
            
        try:
            subprocess.run(
                ["Rscript", wrapper_path], 
                check=True, 
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
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