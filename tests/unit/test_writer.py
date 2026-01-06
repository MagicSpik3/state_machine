import pytest
from spss_engine.state import StateMachine
from code_forge.generator import RGenerator



class TestRGenerator:


    def test_generate_description_file(self):
        """
        Ensure we generate the metadata needed for an R package.
        """
        state = StateMachine()
        writer = RGenerator(state)
        desc = writer.generate_description("MyNewPackage")
        
        assert "Package: MyNewPackage" in desc
        assert "Imports:" in desc
        assert "dplyr" in desc
        assert "lubridate" in desc



    def test_generate_simple_compute(self):
        """
        Scenario: Simple Variable Calculation
        SPSS: COMPUTE Net = Gross - Tax.
        R: mutate(net = gross - tax)
        """
        state = StateMachine()
        state.register_assignment("Net", "COMPUTE Net = Gross - Tax.", dependencies=["GROSS_0", "TAX_0"])
        
        writer = RGenerator(state)
        script = writer.generate_script()
        
        # 1. Check for Libraries
        assert "library(dplyr)" in script
        assert "library(readr)" in script
        
        # 2. Check for Documentation (UPDATED)
        # We now check for standard Roxygen @param tags instead of custom "Data Contract" text
        assert "#' @param df" in script
        assert "#' @export" in script
        
        # 3. Check for Logic
        # Expect lowercase output (snake_case)
        assert "mutate(" in script
        assert "net =" in script
        assert "gross - tax" in script

    def test_generate_conditional_logic(self):
        """
        Scenario: Conditional Assignment
        SPSS: IF (Age >= 18) Status = 1.
        R: mutate(status = if_else(age >= 18, 1, status))
        """
        state = StateMachine()
        src = "IF (Age >= 18) Status = 1."
        state.register_assignment("Status", src, dependencies=["AGE_0"])
        
        writer = RGenerator(state)
        script = writer.generate_script()
        
        # Expect lowercase condition and if_else
        assert "if_else" in script
        assert "age >= 18" in script        
