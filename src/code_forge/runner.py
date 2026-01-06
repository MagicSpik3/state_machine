import os
import csv
import subprocess
import logging
import pandas as pd
from typing import Dict, Optional

logger = logging.getLogger("RRunner")

class RRunner:
    """
    Executes the generated R code to verify it produces the same numbers as SPSS.
    """
    def __init__(self, r_script_path: str):
        self.script_path = os.path.abspath(r_script_path)
        self.work_dir = os.path.dirname(self.script_path)
        
    def run_and_capture(self) -> Dict[str, float]:
        """
        Runs the R script and returns the final row as a dictionary.
        """
        # 1. Create a wrapper script to execute the function
        # We need to source the generated file, create a dummy DF, run it, and print the result.
        wrapper_path = os.path.join(self.work_dir, "run_wrapper.R")
        output_csv = os.path.join(self.work_dir, "r_output.csv")
        
        # We assume the file defines logic_pipeline(df)
        # We create a minimal 1-row dataframe to kickstart the pipeline.
        r_wrapper = f"""
        source("{os.path.basename(self.script_path)}")
        
        # Create a dummy 1-row dataframe
        df <- data.frame(id = 1)
        
        # Run the pipeline
        tryCatch({{
            result <- logic_pipeline(df)
            write.csv(result, "{output_csv}", row.names = FALSE)
        }}, error = function(e) {{
            cat("Error:", e$message)
            quit(status = 1)
        }})
        """
        
        with open(wrapper_path, "w") as f:
            f.write(r_wrapper)
            
        # 2. Execute via Rscript
        try:
            subprocess.run(
                ["Rscript", wrapper_path], 
                check=True, 
                cwd=self.work_dir,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"R Execution Failed: {e.stderr}")
            return {}
            
        # 3. Read the Output
        if not os.path.exists(output_csv):
            return {}
            
        return self._read_first_row(output_csv)

    def _read_first_row(self, csv_path: str) -> Dict[str, float]:
        """Reads the CSV and normalizes keys to UPPERCASE for comparison."""
        results = {}
        try:
            df = pd.read_csv(csv_path)
            if not df.empty:
                # Take the last row (final state)
                row = df.iloc[-1]
                for col in df.columns:
                    # Normalize R's snake_case back to UPPERCASE for comparison with SPSS
                    key = col.upper() 
                    try:
                        val = float(row[col])
                        results[key] = val
                    except (ValueError, TypeError):
                        pass # Ignore non-numeric for now
        except Exception as e:
            logger.error(f"Failed to read R output: {e}")
            
        return results