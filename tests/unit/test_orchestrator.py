import pytest
from unittest.mock import MagicMock, patch
from spec_writer.orchestrator import SpecOrchestrator
from spss_engine.state import StateMachine
from spec_writer.describer import SpecGenerator  # 🟢 Import the Real Component

def test_orchestrator_graph_handoff(tmp_path):
    """
    Strict Integration Test:
    Verifies that SpecOrchestrator correctly coordinates the Pipeline,
    the SpecGenerator, and the GraphGenerator.
    """
    # 1. Setup Mock LLM (The External Boundary)
    # We mock the LLM because we don't want to hit Ollama during tests.
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Generated Spec Content"

    # 2. Setup Orchestrator with Mock LLM
    orchestrator = SpecOrchestrator(llm_client=mock_llm)

    # 3. Inject Real State (Bypassing File Ingest for speed)
    state = StateMachine()
    state.register_assignment("TEST_VAR", "COMPUTE TEST_VAR = 1.", dependencies=[])
    
    # Wire up the Orchestrator's internal components explicitly
    # This replicates what 'ingest()' does, but allows us to skip the file read.
    orchestrator.pipeline.state = state
    
    # 🟢 REAL INTEGRATION: Initialize the real SpecGenerator
    # This tests that Orchestrator and Generator are compatible.
    orchestrator.generator = SpecGenerator(state, mock_llm)

    # 4. Mock ONLY the Graphviz Render (System Call)
    # We patch the class so we can verify the Orchestrator instantiates it correctly.
    with patch("spec_writer.orchestrator.GraphGenerator") as MockGenClass:
        mock_graph_instance = MockGenClass.return_value
        
        # 5. Execute
        out_dir = tmp_path / "docs"
        out_dir.mkdir()
        
        md_path = orchestrator.generate_comprehensive_spec(
            output_dir=str(out_dir), 
            filename_root="test_flow"
        )
        
        # 6. Verify Graph Integration
        # Did Orchestrator pass the REAL state to the GraphGenerator?
        MockGenClass.assert_called_once_with(state)
        # Did it call render?
        assert mock_graph_instance.render.called

        # 7. Verify Spec Integration
        # Did the Orchestrator successfully trigger the SpecGenerator?
        # The file should contain the text returned by our Mock LLM.
        assert "Generated Spec Content" in open(md_path).read()