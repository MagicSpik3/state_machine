import subprocess
import os
import csv
import logging
import pandas as pd
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RRunner:
    """
    Executes generated R code to verify its behavior.
    Wraps the function in a temporary script that imports dependencies
    and runs the logic against provided inputs.
    """

    def __init__(self, script_path: str, r_executable: str = "Rscript"):
        self.script_path = script_path
        self.r_executable = r_executable

    def run_and_capture(self, input_vars: list = None, gold_standard_csv: str = None) -> Dict[str, str]:
        """
        Runs the R script and returns the output variables.
        
        Args:
            input_vars: List of variable names to initialize (Legacy Mode).
            gold_standard_csv: Path to a CSV file containing real input data (Data Bridge Mode).
        """
        directory = os.path.dirname(self.script_path)
        base_name = os.path.basename(self.script_path)
        output_csv = os.path.join(directory, "r_output.csv")
        
        # 1. Generate the Wrapper Script
        wrapper_path = os.path.join(directory, "run_wrapper.R")
        
        # Logic to determine input dataframe source
        if gold_standard_csv and os.path.exists(gold_standard_csv):
            # Safe path handling for R (forward slashes)
            clean_gold_path = gold_standard_csv.replace(os.sep, "/")
            df_init = f'df <- read_csv("{clean_gold_path}", show_col_types = FALSE)'
        else:
            # Legacy fallback: Dummy data
            if not input_vars: input_vars = ["dummy"]
            # Create columns with 0
            cols = ", ".join([f"{v} = 0" for v in input_vars])
            df_init = f'df <- data.frame({cols})'

        wrapper_code = f"""
library(dplyr)
library(readr)
library(lubridate)
library(haven)

# Source the generated logic
source("{base_name}")

# Initialize Data
{df_init}

# Run the Pipeline
tryCatch({{
    result <- logic_pipeline(df)
    
    # Save Result
    write_csv(result, "r_output.csv")
}}, error = function(e) {{
    message("CRITICAL R ERROR: ", e$message)
    quit(status = 1)
}})
"""
        with open(wrapper_path, "w") as f:
            f.write(wrapper_code)

        # 2. Execute R
        cmd = [self.r_executable, wrapper_path]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=directory,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"R Execution Failed:\n{e.stderr}")
            if e.stdout: logger.error(f"R Stdout:\n{e.stdout}")
            raise RuntimeError(f"R execution failed: {e.stderr}")
        finally:
            if os.path.exists(wrapper_path):
                os.remove(wrapper_path)

        # 3. Read Output
        return self._read_first_row(output_csv)

    def _read_first_row(self, csv_path: str) -> Dict[str, str]:
        if not os.path.exists(csv_path):
            return {}
            
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                return {}
            
            # Return first row as dict {COL: VAL}
            first_row = df.iloc[0].to_dict()
            return {str(k).upper(): str(v) for k, v in first_row.items()}
            
        except Exception as e:
            logger.warning(f"Failed to read R output: {e}")
            return {}