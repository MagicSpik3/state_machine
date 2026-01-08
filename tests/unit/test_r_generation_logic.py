import pytest
from spss_engine.state import StateMachine
from code_forge.generator import RGenerator

class TestRGenerationLogic:
    
    def test_recode_to_case_when(self):
        """
        Test A: Verify RECODE commands are transpiled into dplyr::case_when logic.
        Current failure: It likely generates just 'bmi_category = NA' or similar placeholder.
        """
        state = StateMachine()
        
        # Setup: A variable 'bmi' exists
        state.register_assignment("BMI", "COMPUTE bmi = 20.")
        
        # Action: RECODE bmi into categories
        # Note: We use the raw source string that the parser would extract
        recode_cmd = "RECODE bmi (Lo THRU 18.5 = 'Underweight') (18.5 THRU 25 = 'Normal') INTO bmi_category."
        state.register_assignment(
            "BMI_CATEGORY", 
            recode_cmd,
            dependencies=["BMI"]
        )
        
        gen = RGenerator(state)
        script = gen.generate_script()
        
        # Assertions
        print(f"\nGenerated Script Snippet:\n{script}")
        
        assert "case_when" in script, "❌ Logic Missing: RECODE did not generate 'case_when'"
        # Check for loose translation of the logic
        assert "Underweight" in script
        assert "Normal" in script

    def test_variable_object_handling(self):
        """
        Test B: Reproduce the 'VariableVersion object has no attribute rsplit' crash.
        This occurs when generate_description tries to parse variable names for the DESCRIPTION file.
        """
        state = StateMachine()
        state.register_assignment("COMPLEX_VAR_NAME", "COMPUTE COMPLEX_VAR_NAME = 1.")
        
        gen = RGenerator(state)
        
        try:
            # This method analyzes inputs/outputs to write the package DESCRIPTION.
            # It previously crashed because it treated VariableVersion objects as strings.
            description = gen.generate_description("testpkg")
            
            assert "Title: Auto-Generated Logic" in description
            
        except AttributeError as e:
            if "rsplit" in str(e):
                pytest.fail(f"❌ Reproduced Bug: {e}")
            else:
                raise e