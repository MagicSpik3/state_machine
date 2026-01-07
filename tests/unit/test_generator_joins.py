import pytest
from spss_engine.state import StateMachine
from code_forge.generator import RGenerator

class TestRGeneratorJoins:
    
    def test_match_files_to_left_join(self):
        """
        Scenario: MATCH FILES command matches a .sav file.
        SPSS: MATCH FILES /FILE=* /TABLE='benefit_rates.sav' /BY benefit_type.
        R: left_join(benefit_rates, by='benefit_type')
        """
        state = StateMachine()
        join_cmd = "MATCH FILES /FILE=* /TABLE='benefit_rates.sav' /BY benefit_type."
        
        # Register as System Node
        state.register_assignment("###SYS_JOIN_1###", join_cmd, dependencies=[])
        
        gen = RGenerator(state)
        code = gen.generate_script()
        
        assert "left_join(benefit_rates, by='benefit_type')" in code
        assert "benefit_rates = NULL" in code 

    def test_duplicate_joins_skipped(self):
        """
        If the same JOIN appears multiple times, write it once.
        """
        state = StateMachine()
        join_cmd = "MATCH FILES /FILE=* /TABLE='benefit_rates.sav' /BY benefit_type."
        
        state.register_assignment("###SYS_JOIN_1###", join_cmd, dependencies=[])
        state.register_assignment("###SYS_JOIN_2###", join_cmd, dependencies=[])
        
        gen = RGenerator(state)
        code = gen.generate_script()
        
        assert code.count("left_join") == 1