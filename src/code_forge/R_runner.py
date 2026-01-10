import subprocess
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("RRunner")

class RRunner:
    def __init__(self, script_path: str, state_machine=None):
        self.script_path = script_path
        self.work_dir = os.path.dirname(script_path)

    def run_and_capture(self, data_file: Optional[str] = None, loader_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the R script.
        :param data_file: Path to input file (for legacy fallback).
        :param loader_code: Exact R code to load the dataframe (Preferred).
        """
        if not data_file and not loader_code:
            logger.warning("RRunner skipped: No data file or loader code provided.")
            return {}

        wrapper_path = os.path.join(self.work_dir, "wrapper.R")
        output_json = os.path.join(self.work_dir, "r_output.json")
        
        # 1. Generate the harness script
        wrapper_code = self._generate_wrapper(output_json, data_file, loader_code)
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
            if os.path.exists(wrapper_path): os.remove(wrapper_path)
            if os.path.exists(output_json): os.remove(output_json)

    def _generate_wrapper(self, output_path: str, data_file: str, loader_code: str) -> str:
        """
        Generates dynamic R code to load the REAL data and run the pipeline.
        """
        script_name = os.path.basename(self.script_path)
        
        # 🟢 INTELLIGENT LOADING LOGIC
        if loader_code:
            # Use the strict, parser-derived code passed from the engine
            load_cmd = loader_code
        elif data_file:
            # Fallback (Legacy Mode) - Simple guessing
            if data_file.lower().endswith(".sav"):
                load_cmd = f'df <- read_sav("{data_file}")'
            else:
                load_cmd = f'df <- read_csv("{data_file}", show_col_types = FALSE)'
        else:
             load_cmd = "stop('No data source provided')"

        return f"""
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)
        library(jsonlite)

        # 1. Source the Logic
        source("{script_name}")

        tryCatch({{
            # 2. Load Real Data
            {load_cmd}

            # 3. Run Pipeline
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