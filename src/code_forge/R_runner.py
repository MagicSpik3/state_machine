import subprocess
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("RRunner")

class RRunner:
    def __init__(self, script_path: str, state_machine=None):
        # We accept state_machine for compatibility with the caller, 
        # but we don't need it anymore because we trust the SourceInspector.
        self.script_path = script_path
        self.work_dir = os.path.dirname(script_path)

    def run_and_capture(self, data_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the R script using the provided data file.
        """
        if not data_file:
            logger.warning("RRunner skipped: No data file provided for equivalence check.")
            return {}

        wrapper_path = os.path.join(self.work_dir, "wrapper.R")
        output_json = os.path.join(self.work_dir, "r_output.json")
        
        # 1. Generate the harness script
        wrapper_code = self._generate_wrapper(output_json, data_file)
        with open(wrapper_path, "w") as f:
            f.write(wrapper_code)

        # 2. Execute R
        cmd = ["Rscript", "wrapper.R"]
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.work_dir, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"R Execution Failed:\n{result.stderr}")
                return {}

            # 3. Read JSON Output
            if os.path.exists(output_json):
                with open(output_json, "r") as f:
                    return json.load(f)
            else:
                logger.warning("R ran but produced no JSON output.")
                return {}
                
        except Exception as e:
            logger.error(f"R Runner failed: {e}")
            return {}
        finally:
            # Cleanup wrapper to keep the output folder clean
            if os.path.exists(wrapper_path): os.remove(wrapper_path)
            if os.path.exists(output_json): os.remove(output_json)

    def _generate_wrapper(self, output_path: str, data_file: str) -> str:
        """
        Generates simple, robust R code to load the data and run the pipeline.
        """
        script_name = os.path.basename(self.script_path)
        
        # Determine strict loader based on extension
        if data_file.lower().endswith(".sav"):
            load_cmd = f'df <- read_sav("{data_file}")'
        else:
            # Default to CSV for everything else
            load_cmd = f'df <- read_csv("{data_file}", show_col_types = FALSE)'

        return f"""
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)
        library(jsonlite)

        # 1. Source the Logic
        source("{script_name}")

        tryCatch({{
            # 2. Load Real Data (Found by Inspector)
            {load_cmd}

            # 3. Run Pipeline
            # We assume the function is named 'logic_pipeline'
            result <- logic_pipeline(df)

            # 4. Serialize First Row for Comparison
            output_list <- as.list(result[1, ])
            json_out <- toJSON(output_list, auto_unbox = TRUE)
            write(json_out, "{output_path}")

        }}, error = function(e) {{
            message("CRITICAL R ERROR:")
            message(e$message)
            quit(status = 1)
        }})
        """