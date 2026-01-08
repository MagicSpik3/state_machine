import subprocess
import os
import csv
import logging
from typing import Dict, List, Tuple, Set

logger = logging.getLogger(__name__)

class PsppRunner:
    """
    Executes SPSS code using the system 'pspp' binary.
    Returns the data probe AND a list of generated artifacts.
    """

    def __init__(self, executable: str = "pspp"):
        self.executable = executable

    def run_and_probe(self, file_path: str, output_dir: str = ".") -> Tuple[Dict[str, str], List[str]]:
        """
        Runs the SPSS file and returns:
        1. The final values of the first row of data (Probe).
        2. A list of new files generated during execution (Artifacts).
        
        Returns: (Dict {Variable: Value}, List[filename])
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        # 1. Resolve Paths
        abs_file_path = os.path.abspath(file_path)
        abs_output_dir = os.path.abspath(output_dir)
        source_dir = os.path.dirname(abs_file_path)
        
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        csv_path = os.path.join(abs_output_dir, f"{base_name}_probe.csv")
        temp_script_path = os.path.join(abs_output_dir, f"{base_name}_temp.sps")

        # 2. Snapshot Directory State (For Artifact Detection)
        # We look in the output_dir because that's where we run the script
        try:
            pre_files = set(os.listdir(abs_output_dir))
        except FileNotFoundError:
            pre_files = set()

        # 3. Read & Inject Probe
        with open(abs_file_path, 'r') as f:
            original_code = f.read()

        # Save probe to the OUTPUT directory
        csv_path_safe = csv_path.replace(os.sep, "/")
        probe_cmd = f"\nSAVE TRANSLATE /OUTFILE='{csv_path_safe}' /TYPE=CSV /FIELDNAMES /REPLACE.\n"
        
        with open(temp_script_path, 'w') as f:
            f.write(original_code + probe_cmd)

        # 4. Execute PSPP
        # We run inside output_dir so relative paths in SPSS (like SAVE output.csv) land there
        cmd = [self.executable, temp_script_path] 
        
        try:
            subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                cwd=abs_output_dir 
            )
        except subprocess.CalledProcessError as e:
            # Clean up before raising
            if os.path.exists(temp_script_path): os.remove(temp_script_path)
            raise RuntimeError(f"PSPP execution failed: {e.stderr}")

        # 5. Detect Artifacts
        artifacts = []
        try:
            post_files = set(os.listdir(abs_output_dir))
            new_files = post_files - pre_files
            
            probe_name = os.path.basename(csv_path)
            temp_name = os.path.basename(temp_script_path)

            for f in new_files:
                # Ignore the probe CSV and the temp script
                if f == probe_name or f == temp_name:
                    continue
                artifacts.append(f)
        except Exception:
            pass # Non-critical

        # 6. Cleanup
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

        # 7. Read Probe Data
        data = self._read_first_row(csv_path)
        
        return data, artifacts

    def _read_first_row(self, csv_path: str) -> Dict[str, str]:
        if not os.path.exists(csv_path):
            return {}

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            try:
                row = next(reader)
                return {k.strip().upper(): v for k, v in row.items()}
            except StopIteration:
                return {}