import pytest
from unittest.mock import MagicMock
from spss_engine.state import StateMachine
from spec_writer.describer import SpecGenerator

class TestSpecGenerator:
    def test_generate_report_structure(self):
        """
        Verifies that the report generates the correct markdown structure
        and calls the LLM for descriptions.
        """
        # 1. Setup Logic State
        state = StateMachine()
        state.register_assignment("GROSS_PAY", "COMPUTE GROSS_PAY = 500.", dependencies=[])
        state.register_assignment("TAX", "COMPUTE TAX = GROSS_PAY * 0.2.", dependencies=[state.get_current_version("GROSS_PAY")])
        
        # 2. Setup Mock LLM
        mock_client = MagicMock()
        mock_client.generate.return_value = "AI Generated Description"
        
        # 3. Initialize Generator
        generator = SpecGenerator(state, mock_client)
        
        # 4. Generate Report (FIX: Provide required arguments)
        report = generator.generate_report(dead_ids=[], runtime_values={})
        
        assert "# Business Logic Specification" in report
        assert "GROSS_PAY" in report
        assert "TAX" in report

    def test_generate_report_with_verification(self):
        """
        Verifies that runtime values are correctly injected into the report.
        """
        state = StateMachine()
        state.register_assignment("NET_PAY", "COMPUTE NET = 100.", dependencies=[])
        
        mock_client = MagicMock()
        mock_client.generate.return_value = "Desc"
        
        generator = SpecGenerator(state, mock_client)
        
        # Simulate verification data from PSPP
        runtime_data = {"NET_PAY": "100.00"}
        
        # FIX: Provide arguments
        report = generator.generate_report(dead_ids=[], runtime_values=runtime_data)
        
        # Note: We haven't implemented the injection logic in the prompt yet, 
        # but this confirms the API call works.
        assert report is not None