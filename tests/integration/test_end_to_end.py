import pytest
import subprocess
import os
import shutil
import textwrap
from pathlib import Path

STATIFY_SCRIPT = "statify.py" # Assumes this is in root

def test_full_pipeline_with_verification(tmp_path):
    """
    Forensic End-to-End Test
    Run the CLI and capture absolutely everything to diagnose the silent failure.
    """
    # 1. Setup Workspace
    src_dir = tmp_path / "legacy_src"
    dist_dir = tmp_path / "docs_output"
    src_dir.mkdir()
    dist_dir.mkdir()

    # 2. Create Source File
    spss_file = src_dir / "payroll.spss"
    code = textwrap.dedent("""
    DATA LIST LIST /dummy.
    BEGIN DATA
    1
    END DATA.
    COMPUTE Gross = 50000.
    COMPUTE Tax = Gross * 0.2.
    COMPUTE Net = Gross - Tax.
    EXECUTE.
    """)
    spss_file.write_text(code, encoding="utf-8")

    # 3. Environment Setup
    env = os.environ.copy()
    # Ensure src is in pythonpath
    env["PYTHONPATH"] = os.getcwd() + ":" + os.path.join(os.getcwd(), "src")

    # 4. Run CLI
    cmd = [
        "python", STATIFY_SCRIPT,
        str(src_dir),
        "--output", str(dist_dir),
        "--model", "mistral:instruct"
    ]

    print(f"\n🚀 Running: {' '.join(cmd)}")
    
    try:
        # Capture BOTH stdout and stderr
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
        
        # 5. Forensic Report (Print this if the test fails)
        debug_info = f"""
        ================ CLI DIAGNOSTICS ================
        [EXIT CODE]: {result.returncode}
        
        [STDOUT]:
        {result.stdout}
        
        [STDERR]:
        {result.stderr}
        
        [OUTPUT DIR CONTENTS]:
        {list(dist_dir.glob('*'))}
        =================================================
        """
        
        # 6. Verification
        # Check Exit Code
        assert result.returncode == 0, f"CLI Crashed! {debug_info}"
        
        # Check Artifacts
        expected_md = dist_dir / "payroll_spec.md"
        
        if not expected_md.exists():
            pytest.fail(f"Markdown spec missing! {debug_info}")
            
    except subprocess.TimeoutExpired:
        pytest.fail("CLI Timed out after 60s")