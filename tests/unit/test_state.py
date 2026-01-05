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

        assert ver == "AGE_1"  # This confirms they mapped to the same counter

    def test_variable_history_tracking(self):
        """
        Test that the state machine records the 'Provenance' (source code)
        associated with each variable version.
        """
        state = StateMachine()

        # 1. Initial Assignment
        # We now pass the 'raw_code' argument (we will need to update the signature)
        state.register_assignment("Age", source_code="COMPUTE Age = 25.")

        # 2. Re-assignment
        state.register_assignment("Age", source_code="COMPUTE Age = 26.")

        # 3. Retrieve History
        history = state.get_history("Age")

        assert len(history) == 2
        assert history[0].id == "AGE_0"
        assert history[0].source == "COMPUTE Age = 25."

        assert history[1].id == "AGE_1"
        assert history[1].source == "COMPUTE Age = 26."
