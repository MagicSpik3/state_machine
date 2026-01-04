import pytest
from spss_engine.state import StateMachine

class TestStateMachine:

    def test_initial_assignment(self):
        """Test that a new variable gets version 0 and is normalized."""
        state = StateMachine()
        ver = state.register_assignment("Age")
        
        # Expect UPPERCASE normalization
        assert ver == "AGE_0"
        assert state.get_current_version("Age") == "AGE_0"

    def test_reassignment_ssa(self):
        """Test that updating a variable increments its version (SSA)."""
        state = StateMachine()
        
        # First assignment: x = 1
        v1 = state.register_assignment("x")
        assert v1 == "X_0"  # Normalized to X
        
        # Second assignment: x = 2
        v2 = state.register_assignment("x")
        assert v2 == "X_1"
        
        # Ensure history is preserved (conceptually)
        assert state.get_current_version("x") == "X_1"

    def test_case_insensitivity(self):
        """SPSS variables are case-insensitive. 'AGE' and 'Age' are the same."""
        state = StateMachine()
        state.register_assignment("AGE")
        ver = state.register_assignment("Age")
        
        assert ver == "AGE_1" # This confirms they mapped to the same counter