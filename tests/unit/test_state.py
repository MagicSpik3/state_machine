import pytest
from spss_engine.state import StateMachine

class TestStateMachine:

    def test_initial_assignment(self):
        sm = StateMachine()
        sm.register_assignment("Age", source_code="COMPUTE Age=1.")
        assert sm.get_current_version("Age") == "AGE_0"

    def test_reassignment_ssa(self):
        sm = StateMachine()
        sm.register_assignment("Age", source_code="COMPUTE Age=1.") # AGE_0
        sm.register_assignment("Age", source_code="COMPUTE Age=2.") # AGE_1
        
        assert sm.get_current_version("Age") == "AGE_1"
        
        history = sm.get_history("Age")
        assert len(history) == 2
        assert history[0].id == "AGE_0"
        assert history[1].id == "AGE_1"

    def test_case_insensitivity(self):
        sm = StateMachine()
        sm.register_assignment("age", source_code="COMPUTE age=1.")
        assert sm.get_current_version("AGE") == "AGE_0"

    def test_undefined_variable(self):
        sm = StateMachine()
        with pytest.raises(ValueError):
            sm.get_current_version("Ghost")

    # --- THE MISSING TEST ---
    def test_variable_history_tracking(self):
        """
        Test that the state machine records the 'Provenance' (source code)
        associated with each variable version.
        """
        state = StateMachine()

        # 1. Initial Assignment
        state.register_assignment("Age", source_code="COMPUTE Age = 25.")

        # 2. Re-assignment
        state.register_assignment("Age", source_code="COMPUTE Age = 26.")

        # 3. Retrieve History
        history = state.get_history("Age")

        assert len(history) == 2
        
        # Check Version 0
        assert history[0].id == "AGE_0"
        assert history[0].source == "COMPUTE Age = 25."

        # Check Version 1
        assert history[1].id == "AGE_1"
        assert history[1].source == "COMPUTE Age = 26."