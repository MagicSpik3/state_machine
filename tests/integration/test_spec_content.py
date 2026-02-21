import os
import pytest
from spec_writer.orchestrator import SpecOrchestrator
from common.llm import OllamaClient
from unittest.mock import MagicMock

class TestSpecContent:
    """
    End-to-End Integration Test.
    Verifies that the generated Markdown Specification accurately reflects
    the Input/Output contracts defined in the source SPSS.
    """
    
    def test_spec_contains_io_contracts(self, tmp_path):
        # 1. Create a dummy SPSS file with clear I/O
        # We use a temp directory so we don't clutter the repo
        d = tmp_path / "spss_src"
        d.mkdir()
        p = d / "test_io.sps"
        
        # This script has 1 Input (CSV with schema) and 1 Output (SAV)
        p.write_text("""
        GET DATA
          /TYPE=TXT
          /FILE="contract_input.csv"
          /VARIABLES=
            customer_id F8.0
            signup_date ADATE10.
            
        COMPUTE flag=1.
        
        SAVE OUTFILE='contract_output.sav'.
        """, encoding="utf-8")
        
        # 2. Setup Orchestrator
        # We Mock the LLM because we aren't testing the *quality* of the prose,
        # just the *presence* of the structural data (tables, filenames).
        mock_llm = MagicMock(spec=OllamaClient)
        mock_llm.generate.return_value = "AI Generated Description"
        
        orchestrator = SpecOrchestrator(llm_client=mock_llm)
        
        # 3. Run Ingestion (This parses the file and builds the State)
        orchestrator.ingest(str(p))
        
        # 4. Generate the Spec
        output_dir = tmp_path / "docs"
        orchestrator.generate_comprehensive_spec(str(output_dir), "integration_test")
        
        # 5. Verify the Artifacts
        spec_path = output_dir / "integration_test_spec.md"
        assert spec_path.exists()
        
        content = spec_path.read_text(encoding="utf-8")
        
        # --- ASSERTIONS ---
        
        # A. Check Input Data Contract (The Table)
        assert "contract_input.csv" in content
        # Verify columns are extracted and documented
        assert "| **customer_id** | Numeric | `F8.0` |" in content
        assert "| **signup_date** | Date | `ADATE10` |" in content
        
        # B. Check Logic Presence
        assert "COMPUTE flag=1" in content
        
        # C. Check Output Data (The filename must appear)
        assert "contract_output.sav" in content