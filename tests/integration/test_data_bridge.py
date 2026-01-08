import pytest
import os
import shutil
from pathlib import Path
from spss_engine.inspector import SourceInspector
from spss_engine.spss_runner import PsppRunner

def test_data_bridge_lifecycle(tmp_path):
    """
    Integration: Verifies the full lifecycle of data bridging.
    1. Scan SPSS for inputs/outputs.
    2. Copy inputs to the execution sandbox.
    3. Run PSPP to generate 'Gold Standard'.
    4. Archive the gold standard for later comparison.
    """
    
    # 1. Setup: Create a Mock Legacy Environment
    legacy_src_dir = tmp_path / "legacy_src"
    legacy_src_dir.mkdir()
    
    target_dir = tmp_path / "target_output"
    target_dir.mkdir()
    
    # Create the Input Data (The "Asset" we must transport)
    input_csv = legacy_src_dir / "data.csv"
    input_csv.write_text("id,val\n1,100\n2,200", encoding="utf-8")
    
    # Create the SPSS Script
    # Note: We assume the SPSS expects data.csv in its current working directory
    spss_script = legacy_src_dir / "pipeline.spss"
    code = """
    GET DATA /TYPE=TXT /FILE='data.csv' /ARRANGEMENT=DELIMITED /FIRSTCASE=2 /VARIABLES=id F4.0 val F4.0.
    COMPUTE val = val * 2.
    SAVE TRANSLATE /OUTFILE='out_file.csv' /TYPE=CSV /REPLACE.
    """
    spss_script.write_text(code, encoding="utf-8")

    # -------------------------------------------------------------------------
    # Phase 1: Inspection (The logic we just added)
    # -------------------------------------------------------------------------
    inspector = SourceInspector()
    inputs, outputs = inspector.scan(code)
    
    assert "data.csv" in inputs
    assert "out_file.csv" in outputs
    
    # -------------------------------------------------------------------------
    # Phase 2: Transport (Simulating what statify.py must do)
    # -------------------------------------------------------------------------
    # Copy detected inputs from source to target
    for filename in inputs:
        src = legacy_src_dir / filename
        dst = target_dir / filename
        if src.exists():
            shutil.copy(src, dst)
        else:
            pytest.fail(f"Expected input file missing: {src}")
            
    assert (target_dir / "data.csv").exists(), "Input CSV was not copied to target"

    # -------------------------------------------------------------------------
    # Phase 3: Execution (Generating the Gold Standard)
    # -------------------------------------------------------------------------
    runner = PsppRunner()
    # Run in the TARGET dir, so output appears there
    # We pass the target_dir as the 'output_dir' logic, effectively running inside the sandbox
    
    # Manually run PSPP logic to control the CWD to target_dir
    # (Since PsppRunner usually runs in source dir, we mimic the file movement here)
    temp_script = target_dir / "pipeline.spss"
    shutil.copy(spss_script, temp_script)
    
    # We call run_and_probe pointing to the SANDBOX script
    data, artifacts = runner.run_and_probe(str(temp_script), str(target_dir))
    
    # -------------------------------------------------------------------------
    # Phase 4: Archival (The critical requirement)
    # -------------------------------------------------------------------------
    # We expect 'out_file.csv' to exist in target_dir now
    generated_output = target_dir / "out_file.csv"
    assert generated_output.exists(), "PSPP failed to generate output CSV"
    
    # Rename for safekeeping (Gold Standard)
    archived_output = target_dir / "out_file_original.csv"
    shutil.move(generated_output, archived_output)
    
    assert archived_output.exists()
    assert not generated_output.exists() # Ensure original name is free for R to use