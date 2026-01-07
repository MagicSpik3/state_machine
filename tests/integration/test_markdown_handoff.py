import pytest
import os
from unittest.mock import MagicMock
from spec_writer.orchestrator import SpecOrchestrator
from spss_engine.state import StateMachine

def test_orchestrator_markdown_handoff(tmp_path):
    """
    Targeted Verification:
    Ensures SpecOrchestrator calls SpecGenerator.generate_report() 
    and successfully writes the output to a file.
    """
    # 1. Setup Orchestrator with Mock LLM
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Run logic description."
    
    orchestrator = SpecOrchestrator(llm_client=mock_llm)
    
    # 2. Inject Dummy State (Bypass parsing)
    state = StateMachine()
    state.register_assignment("TEST_VAR", "COMPUTE TEST_VAR = 1.", dependencies=[])
    orchestrator.pipeline.state_machine = state
    
    # Manually trigger ingest's side effect (initializing the generator)
    # We can't call ingest() because it requires a real file.
    # So we initialize the generator manually as ingest() would.
    from spec_writer.describer import SpecGenerator
    orchestrator.generator = SpecGenerator(state, mock_llm)

    # 3. Execute
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    
    # Run the full generation flow
    orchestrator.generate_comprehensive_spec(str(output_dir), "handoff_test")

    # 4. Verify Markdown Artifact
    expected_md = output_dir / "handoff_test_spec.md"
    
    assert expected_md.exists(), "Markdown file was not created"
    
    content = expected_md.read_text()
    assert "# Business Logic Specification" in content
    assert "Run logic description" in content
    
    # 5. Verify Graph Handoff didn't break (sanity check)
    expected_png = output_dir / "handoff_test_flow.png"
    assert expected_png.exists(), "Graph PNG was not created alongside Markdown"