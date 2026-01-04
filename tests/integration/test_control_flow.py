import pytest
from spss_engine.pipeline import CompilerPipeline

class TestControlFlow:

    def test_flag_variable_nightmare(self):
        """
        Scenario: The 'Flag Variable' Anti-Pattern.
        A single variable 'x' is repurposed repeatedly to control logic flow.
        
        Logic:
        1. x = 2 (Even) -> Should trigger 'Do Q' logic
        2. x = 3 (Odd)  -> Should trigger 'Do P' logic
        
        The State Machine must track 'x' as distinct versions so we know 
        WHICH 'x' was active during specific operations.
        """
        
        # Simulating the messy code
        code = """
        * Phase 1: Set Control Flag to 2 (Even Mode).
        COMPUTE x = 2.
        
        * Logic Block A (Should happen because x=2).
        IF (x = 2) COMPUTE Result_A = 100.
        
        * Phase 2: Reuse Control Flag (Set to 3).
        COMPUTE x = 3.
        
        * Logic Block B (Should happen because x=3).
        IF (x = 3) COMPUTE Result_B = 200.
        
        * Phase 3: Reuse again.
        COMPUTE x = 4.
        """
        
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        # 1. Verify SSA Versioning of the Control Variable
        # We expect x to have evolved: x_0 (2), x_1 (3), x_2 (4)
        history_x = pipeline.get_variable_history("x")
        
        assert len(history_x) == 3
        assert history_x[0].id == "X_0"
        assert "x = 2" in history_x[0].source
        
        assert history_x[1].id == "X_1"
        assert "x = 3" in history_x[1].source
        
        assert history_x[2].id == "X_2"
        assert "x = 4" in history_x[2].source
        
        # 2. Verify the Dependent Logic
        # Result_A should depend on the state where x was valid.
        # Currently, our extractor is naive (doesn't link dependencies yet),
        # but we CAN verify that Result_A and Result_B were recognized and versioned.
        assert pipeline.get_variable_version("Result_A") == "RESULT_A_0"
        assert pipeline.get_variable_version("Result_B") == "RESULT_B_0"