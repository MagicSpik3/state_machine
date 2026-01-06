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
        state.register_assignment("TAX", "COMPUTE TAX = GROSS_PAY * 0.2.", dependencies=["GROSS_PAY_0"])
        
        # 2. Setup Mock LLM
        # We replace the real OllamaClient with a MagicMock
        mock_client = MagicMock()
        mock_client.generate.return_value = "AI Generated Description"
        
        # 3. Initialize Generator
        generator = SpecGenerator(state, mock_client)
        
        # 4. Generate Report
        report = generator.generate_report()
        
        # 5. Assertions
        assert "# Business Logic Specification" in report
        assert "## Chapter" in report
        
        # Verify Variables are listed
        assert "GROSS_PAY" in report
        assert "TAX" in report
        
        # Verify AI content was injected
        assert "AI Generated Description" in report
        
        # Verify the Generator actually called the AI
        assert mock_client.generate.called
        assert mock_client.generate.call_count >= 2 # Once for Title, Once per Node

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
        
        report = generator.generate_report(runtime_values=runtime_data)
        
        assert "✅ Verified Execution" in report
        assert "*Example Value: `100.00`*" in report