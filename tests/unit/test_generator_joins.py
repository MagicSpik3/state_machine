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
        
        # Simulate a variable (e.g., 'weekly_rate') that is associated with this Join command
        join_cmd = "MATCH FILES /FILE=* /TABLE='benefit_rates.sav' /BY benefit_type."
        state.register_assignment("weekly_rate", join_cmd, dependencies=[])
        
        gen = RGenerator(state)
        code = gen.generate_script()
        
        assert "left_join(benefit_rates, by='benefit_type')" in code

    def test_duplicate_joins_skipped(self):
        """
        If 5 variables come from the same JOIN, we should only write the left_join() line ONCE.
        """
        state = StateMachine()
        join_cmd = "MATCH FILES /FILE=* /TABLE='benefit_rates.sav' /BY benefit_type."
        
        # Two variables from same join
        state.register_assignment("weekly_rate", join_cmd)
        state.register_assignment("description", join_cmd)
        
        gen = RGenerator(state)
        code = gen.generate_script()
        
        # We expect exactly one occurrence of left_join
        assert code.count("left_join") == 1