import pytest
import os
from unittest.mock import MagicMock, patch
from spec_writer.orchestrator import SpecOrchestrator
from spss_engine.state import VariableVersion

class TestSpecOrchestrator:
    """
    Verifies the coordination logic: Ingest -> Compile -> Generate -> Save.
    Fills the gap identified in the Architecture Map.
    """

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.generate.return_value = "AI Description"
        return llm

    def test_full_orchestration_flow(self, tmp_path, mock_llm):
        # 1. Setup
        orchestrator = SpecOrchestrator(llm_client=mock_llm)
        
        # Create a dummy SPSS file
        spss_file = tmp_path / "test.spss"
        spss_file.write_text("COMPUTE x = 1.", encoding="utf-8")
        
        # 2. Ingest (Should run Pipeline)
        orchestrator.ingest(str(spss_file))
        
        assert len(orchestrator.pipeline.state_machine.nodes) > 0, "Pipeline failed to process file"
        assert orchestrator.generator is not None, "Generator was not initialized"

        # 3. Generate (Should run Generator)
        output_dir = tmp_path / "out"
        md_file = orchestrator.generate_comprehensive_spec(str(output_dir), "test_doc")
        
        # 4. Verify Artifacts
        assert os.path.exists(md_file)
        with open(md_file, 'r') as f:
            content = f.read()
            assert "Business Logic Specification" in content
            assert "COMPUTE x = 1." in content # Source code should be present

    def test_missing_ingest_guard(self, tmp_path):
        """Ensure we can't generate specs without data."""
        orchestrator = SpecOrchestrator()
        
        with pytest.raises(ValueError) as exc:
            orchestrator.generate_comprehensive_spec(str(tmp_path), "fail")
        
        assert "Call ingest() first" in str(exc.value)