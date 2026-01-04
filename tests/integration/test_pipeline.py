import pytest
from spss_engine.pipeline import CompilerPipeline

class TestEndToEndPipeline:

    def test_simple_linear_flow(self):
        """
        Scenario: A simple script with sequential assignments.
        Goal: Verify that variables are detected and versioned correctly (SSA).
        """
        spss_code = """
        * Initialize variables.
        COMPUTE Age = 25.
        COMPUTE Income = 50000.
        
        * Update Age (should trigger new version).
        COMPUTE Age = 26.
        """
        
        # 1. Initialize the Pipeline
        pipeline = CompilerPipeline()
        
        # 2. Run the code
        pipeline.process(spss_code)
        
        # 3. Verify State
        # Age was assigned twice (initially 0, then 1)
        assert pipeline.get_variable_version("Age") == "AGE_1"
        
        # Income was assigned once
        assert pipeline.get_variable_version("Income") == "INCOME_0"

    def test_mixed_commands_flow(self):
        """
        Scenario: Mixed commands (IF, RECODE, EXECUTE).
        Goal: Verify parsing correctly ignores flow control for now 
              but picks up assignments inside them.
        """
        spss_code = """
        STRING Status (A10).
        COMPUTE Valid = 0.
        
        IF (Valid = 0)
            RECODE Status ('Active'='Inactive').
            
        EXECUTE.
        """
        
        pipeline = CompilerPipeline()
        pipeline.process(spss_code)
        
        # STRING Status -> STATUS_0
        # RECODE Status -> STATUS_1 (Because RECODE counts as assignment)
        assert pipeline.get_variable_version("Status") == "STATUS_1"
        assert pipeline.get_variable_version("Valid") == "VALID_0"