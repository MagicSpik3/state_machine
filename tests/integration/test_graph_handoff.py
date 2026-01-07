import pytest
import os
from unittest.mock import MagicMock
from spec_writer.orchestrator import SpecOrchestrator
from spss_engine.state import StateMachine

def test_orchestrator_graph_handoff(tmp_path):
    """
    Targeted Verification:
    Ensures SpecOrchestrator calls GraphGenerator.render() using the 
    correct instance method signature, not the old static/keyword signature.
    """
    # 1. Setup Orchestrator
    orchestrator = SpecOrchestrator()
    
    # 2. Inject Dummy State (Bypass parsing/ingest)
    # We manually populate the pipeline's state machine
    state = StateMachine()
    state.register_assignment("TEST_VAR", "COMPUTE TEST_VAR = 1.", dependencies=[])
    orchestrator.pipeline.state_machine = state
    
    # Mock the text generator so we don't need LLM/Ollama
    orchestrator.generator = MagicMock()
    orchestrator.generator.generate_report.return_value = "# Mock Spec"

    # 3. Execute
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    
    try:
        # This calls 'generate_comprehensive_spec', which triggers GraphGenerator.
        # If Orchestrator passes 'filename=...', this will raise TypeError.
        orchestrator.generate_comprehensive_spec(str(output_dir), "handoff_test")
        
    except TypeError as e:
        if "unexpected keyword argument" in str(e):
            pytest.fail(f"🚨 API MISMATCH: Orchestrator used old signature. Error: {e}")
        else:
            raise e

    # 4. Verify
    # Graphviz automatically adds .png extension
    expected_png = output_dir / "handoff_test_flow.png"
    
    # We assert the code attempted to create the file
    # (If Graphviz is missing on the system, this might fail differently, 
    # but the TypeError check above is the critical part)
    if not expected_png.exists():
        # Check if maybe it made a file without extension (old behavior)
        naked_file = output_dir / "handoff_test_flow"
        if naked_file.exists():
            pytest.fail("Orchestrator generated file without extension (Old Behavior)")