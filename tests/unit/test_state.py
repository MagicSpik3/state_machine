import pytest
from spss_engine.state import StateMachine, VariableVersion

class TestStateMachine:
    def test_initial_assignment(self):
        sm = StateMachine()
        # FIX: Changed source_code -> source
        node = sm.register_assignment("age", source="COMPUTE age = 25.", dependencies=[])
        
        assert node.name == "AGE"
        assert node.version == 0
        assert node.id == "AGE_0"
        assert len(sm.get_history("age")) == 1

    def test_reassignment_ssa(self):
        sm = StateMachine()
        sm.register_assignment("status", source="COMPUTE status = 1.", dependencies=[])
        # FIX: Changed source_code -> source
        sm.register_assignment("status", source="COMPUTE status = 2.", dependencies=[])
        
        history = sm.get_history("status")
        assert len(history) == 2
        assert history[0].id == "STATUS_0"
        assert history[1].id == "STATUS_1"

    def test_case_insensitivity(self):
        sm = StateMachine()
        sm.register_assignment("Gross", source="...", dependencies=[])
        # FIX: Changed source_code -> source
        sm.register_assignment("GROSS", source="...", dependencies=[])
        
        assert len(sm.get_history("gross")) == 2

    def test_variable_history_tracking(self):
        sm = StateMachine()
        v1 = sm.register_assignment("A", source="...", dependencies=[])
        v2 = sm.register_assignment("A", source="...", dependencies=[])
        
        assert sm.get_current_version("A") == v2