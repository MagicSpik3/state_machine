import pytest
from unittest.mock import MagicMock, patch
from spec_writer.orchestrator import SpecOrchestrator
from spss_engine.state import StateMachine
from spec_writer.describer import SpecGenerator  # 🟢 Import Real Component

def test_orchestrator_graph_handoff(tmp_path):
    """
    Strict Integration Test:
    Verifies that SpecOrchestrator correctly coordinates the Pipeline,
    the SpecGenerator, and the GraphGenerator.
    """
    # 1. Setup Mock LLM (The External Boundary)
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Generated Spec Content"

    # 2. Setup Orchestrator
    orchestrator = SpecOrchestrator(llm_client=mock_llm)

    # 3. Inject Real State (Bypass parsing/ingest)
    state = StateMachine()
    state.register_assignment("TEST_VAR", "COMPUTE TEST_VAR = 1.", dependencies=[])
    
    # Wire up the Orchestrator's internal pipeline state
    # We use .state directly because we removed the .state_machine alias
    orchestrator.pipeline.state = state
    
    # 🟢 CRITICAL FIX: MANUALLY INJECT THE GENERATOR
    # The Orchestrator throws ValueError if this is None.
    # Since we skipped ingest(), we must create it manually here.
    orchestrator.generator = SpecGenerator(state, mock_llm)

    # 4. Mock ONLY the Graphviz Render (System Call)
    with patch("spec_writer.orchestrator.GraphGenerator") as MockGenClass:
        mock_graph_instance = MockGenClass.return_value
        
        # 5. Execute
        out_dir = tmp_path / "docs"
        out_dir.mkdir()
        
        # This will now succeed because self.generator is set
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
        # Did the generated file contain the text returned by our Mock LLM?
        assert "Generated Spec Content" in open(md_path).read()