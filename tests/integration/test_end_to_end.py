import pytest
import os
import shutil
import subprocess
import textwrap

# We invoke the statify script via subprocess to test the CLI interface properly
STATIFY_SCRIPT = "statify.py"

@pytest.fixture
def workspace(tmp_path):
    """Sets up a clean workspace with a 'src' and 'dist' folder."""
    src = tmp_path / "legacy_src"
    src.mkdir()
    
    dist = tmp_path / "docs_output"
    dist.mkdir()
    
    return src, dist

def test_full_pipeline_with_verification(workspace):
    """
    Scenario:
    1. User has a payroll.spss file in legacy_src/
    2. User runs `statify legacy_src/ --output docs_output/`
    3. System should:
       - Compile Graph
       - Run PSPP (if installed)
       - Generate PNG
       - Generate Markdown with verification badge
    """
    src_dir, dist_dir = workspace
    
    # 1. Create Source File
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
    
    # 2. Run Statify CLI
    # We use the Mock LLM via environment variable or just let it run if Ollama is there.
    # To keep this test deterministic without requiring Ollama, we can't easily mock the CLI 
    # unless we import the main function. 
    # For now, let's assume if it crashes on Ollama connection, we'll see it.
    
    # Note: This test requires PYTHONPATH to be set.
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + ":" + os.path.join(os.getcwd(), "src")
    
    cmd = [
        "python", STATIFY_SCRIPT, 
        str(src_dir), 
        "--output", str(dist_dir),
        "--model", "mistral:instruct" # Hopefully local, or it will just timeout/error gracefully
    ]
    
    # If Ollama isn't running, this might hang or fail. 
    # Ideally, we'd use a flag to swap to MockLLM for CLI tests, but for now let's try running it.
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
        
        # Check standard success
        assert result.returncode == 0, f"CLI Failed: {result.stderr}"
        
        # 3. Check Artifacts
        expected_md = dist_dir / "payroll_spec.md"
        expected_png = dist_dir / "payroll_flow.png"
        
        assert expected_md.exists(), "Markdown spec was not generated"
        assert expected_png.exists(), "PNG graph was not generated"
        
        # 4. Verify Content
        content = expected_md.read_text(encoding="utf-8")
        
        # Check for Verified Badge (Only if PSPP is installed)
        if shutil.which("pspp"):
            assert "Verified Execution" in content
            assert "Example Value: `40000" in content  # Net Pay check
            
    except subprocess.TimeoutExpired:
        pytest.fail("Statify execution timed out (Likely Ollama or PSPP hanging)")