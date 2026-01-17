import pytest
from spss_engine.state import StateMachine, InputSchema, ColumnSchema
from code_forge.generator import RGenerator
from spec_writer.describer import SpecGenerator
from common.llm import OllamaClient
from unittest.mock import MagicMock

class TestSchemaFlow:
    """
    Integration test that flows a Schema through Generation and Documentation
    to ensure all new branches are covered.
    """

    @pytest.fixture
    def populated_state(self):
        """Creates a StateMachine with a rich InputSchema."""
        state = StateMachine()
        
        # Register a complex contract
        state.register_input(
            filename="survey_data.csv",
            fmt="CSV",
            delimiter="\t",
            raw_vars=[
                ("respondent_id", "F8.0"),       # Numeric
                ("zip_code", "A5"),              # String
                ("interview_date", "ADATE10")    # Date
            ]
        )
        
        # Add some dummy logic so the describer has clusters to process
        state.register_assignment("flag", "COMPUTE flag=1.", [])
        state.reset_scope() # Finalize cluster
        
        return state

    def test_r_generator_type_enforcement(self, populated_state):
        """
        Verifies generator.py produces specific type casting lines.
        Target: Coverage for _generate_type_enforcement logic.
        """
        gen = RGenerator(populated_state)
        script = gen.generate_script()
        
        # Check for the Schema Header
        assert "# --- Schema Type Enforcement ---" in script
        
        # Check Numeric Cast
        assert "df$respondent_id <- as.numeric(df$respondent_id)" in script
        
        # Check String Cast
        assert "df$zip_code <- as.character(df$zip_code)" in script
        
        # Check Date Cast
        assert "df$interview_date <- as.Date(df$interview_date, format='%d-%b-%Y')" in script

    def test_spec_generator_data_dictionary(self, populated_state):
        """
        Verifies describer.py includes the Data Contract section.
        Target: Coverage for Schema iteration in generate_report.
        """
        # Mock LLM to avoid external calls
        mock_llm = MagicMock(spec=OllamaClient)
        mock_llm.generate.return_value = "Mock Description"
        
        writer = SpecGenerator(populated_state, mock_llm)
        report = writer.generate_report()
        
        # Check Section Headers
        assert "## 1. Data Contracts (Inputs)" in report
        assert "### 📄 Dataset: `survey_data.csv`" in report
        
        # Check Table Content
        assert "| **respondent_id** | Numeric | `F8.0` |" in report
        assert "| **zip_code** | String | `A5` |" in report
        assert "| **interview_date** | Date | `ADATE10` |" in report