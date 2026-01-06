import pytest
from unittest.mock import MagicMock, patch
from spss_engine.state import StateMachine
from code_forge.generator import RGenerator
from code_forge.refiner import CodeRefiner
import requests

class TestRefinementFlow:
    """
    Integration test verifying the interaction between:
    1. RGenerator (The Source)
    2. CodeRefiner (The Middleware)
    3. OllamaClient (The AI Service)
    """

    @patch('code_forge.refiner.OllamaClient')
    def test_end_to_end_refinement_success(self, MockClientClass):
        """
        Scenario: The AI successfully polishes the rough code.
        """
        # 1. Setup the 'Rough' State
        state = StateMachine()
        # Create a legacy variable. The Generator will output this naively.
        state.register_assignment("X", "COMPUTE X = 1.", dependencies=[])
        
        # 2. Setup the AI Mock
        # We want to prove the Refiner actually calls the LLM with the generator's output.
        mock_instance = MockClientClass.return_value
        mock_instance.generate.return_value = "df %>% mutate(x = 1) # AI POLISHED THIS"

        # 3. Execute the Pipeline Components (Manually, like statify.py does)
        # Step A: Generate
        generator = RGenerator(state)
        rough_draft = generator.generate_script()
        
        # Step B: Refine
        refiner = CodeRefiner()
        final_code = refiner.refine(rough_draft)

        # 4. Assertions
        # Verify the Refiner 'saw' the rough draft
        assert "logic_pipeline" in rough_draft
        
        # Verify the Refiner called the LLM
        mock_instance.generate.assert_called_once()
        
        # Check the arguments passed to the LLM (Integration Check)
        # The prompt sent to the AI must contain the code from the Generator
        call_args = mock_instance.generate.call_args[0][0]
        assert rough_draft in call_args
        
        # Verify the Output is the 'Polished' version
        assert final_code == "df %>% mutate(x = 1) # AI POLISHED THIS"

    @patch('code_forge.refiner.OllamaClient')
    def test_end_to_end_refinement_failure_fallback(self, MockClientClass):
        """
        Scenario: The AI crashes/times out.
        Crucial Safety Check: The pipeline must NOT crash; it must return the rough draft.
        """
        # 1. Setup
        state = StateMachine()
        state.register_assignment("Y", "COMPUTE Y = 2.", dependencies=[])
        
        # 2. Setup the AI Mock to FAIL
        mock_instance = MockClientClass.return_value
        mock_instance.generate.side_effect = requests.exceptions.ReadTimeout("AI went to sleep")

        # 3. Execute
        generator = RGenerator(state)
        rough_draft = generator.generate_script()
        
        refiner = CodeRefiner()
        final_code = refiner.refine(rough_draft)

        # 4. Assertions
        # The Refiner should have caught the error and returned the original code
        assert final_code == rough_draft
        assert "logic_pipeline" in final_code
        # Ensure it didn't return an error message or empty string
        assert "AI Error" not in final_code