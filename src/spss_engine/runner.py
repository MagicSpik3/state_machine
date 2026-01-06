import subprocess
import os
import csv
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PsppRunner:
    """
    Executes SPSS code using the system 'pspp' binary and captures the output state.
    """

    def __init__(self, executable: str = "pspp"):
        self.executable = executable


    def run_and_probe(self, file_path: str, output_dir: str = ".") -> Dict[str, str]:
        """
        Runs the SPSS file and returns the final values of the first row of data.
        Returns: Dict {Variable: Value}
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        # 1. Resolve Paths
        # We need absolute paths because we are going to change the CWD
        abs_file_path = os.path.abspath(file_path)
        abs_output_dir = os.path.abspath(output_dir)
        source_dir = os.path.dirname(abs_file_path)
        
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        csv_path = os.path.join(abs_output_dir, f"{base_name}_probe.csv")
        temp_script_path = os.path.join(abs_output_dir, f"{base_name}_temp.sps")

        # 2. Read Original Code
        with open(abs_file_path, 'r') as f:
            original_code = f.read()

        # 3. Inject "The Probe"
        # Note: We must use the ABSOLUTE path for the probe output, 
        # because PSPP will be running inside 'source_dir', but we want output in 'docs/'
        # Windows/PSPP sometimes struggles with paths, but forward slashes usually work.
        csv_path_safe = csv_path.replace(os.sep, "/")
        
        probe_cmd = f"\nSAVE TRANSLATE /OUTFILE='{csv_path_safe}' /TYPE=CSV /FIELDNAMES /REPLACE.\n"
        
        with open(temp_script_path, 'w') as f:
            f.write(original_code + probe_cmd)

        # 4. Execute PSPP
        # FIX: Removed "-b". 
        # The legacy code uses "Interactive" style syntax (subcommands in col 1, explicit dots).
        # -b enforces "Batch" rules (indentation required), which causes the crash.
        cmd = [self.executable, temp_script_path] 
               
        try:
            # FIX: Set cwd=source_dir so PSPP finds local CSVs (control_vars.csv, etc.)
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                cwd=source_dir 
            )
            logger.info(f"PSPP Execution successful for {base_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"PSPP Failed:\n{e.stderr}")
            # If it failed, check if it printed anything to stdout (syntax errors often go there)
            if e.stdout: logger.error(f"PSPP Output:\n{e.stdout}")
            raise RuntimeError(f"PSPP execution failed: {e.stderr}")
        finally:
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)

        # 5. Read the Probe (CSV)
        return self._read_first_row(csv_path)



    def _read_first_row(self, csv_path: str) -> Dict[str, str]:
        if not os.path.exists(csv_path):
            return {}

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            # The CSV will now have headers: "DUMMY,GROSS,TAX_RATE..."
            reader = csv.DictReader(f)

            # Since fieldnames are inferred from the first row,
            # we need to normalize them (strip whitespace, upper case)
            # if PSPP does something funky. But usually DictReader handles the keys.

            try:
                row = next(reader)
                # Normalize keys to Upper Case to match our Engine
                return {k.strip().upper(): v for k, v in row.items()}
            except StopIteration:
                return {}
