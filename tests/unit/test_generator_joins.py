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
        
        # 🟢 FIX: Explicitly pass the lookup. The Generator no longer 'discovers' it.
        # This simulates the Inspector passing data to the Generator.
        code = gen.generate_script(lookups=['benefit_rates.sav'])
        
        # 1. Check Logic Generation
        assert "left_join(benefit_rates, by='benefit_type')" in code
        
        # 2. Check Signature Generation
        assert "benefit_rates = NULL" in code

    def test_duplicate_joins_signature(self):
        """
        If the same JOIN appears multiple times in the logic,
        the FUNCTION SIGNATURE should still only list the argument once.
        (Body duplication is allowed/expected if the State Machine has duplicate nodes).
        """
        state = StateMachine()
        join_cmd = "MATCH FILES /FILE=* /TABLE='lookup.sav' /BY id."
        
        # Register two separate nodes with the same command
        state.register_assignment("###SYS_JOIN_1###", join_cmd, dependencies=[])
        state.register_assignment("###SYS_JOIN_2###", join_cmd, dependencies=[])
        
        gen = RGenerator(state)
        
        # 🟢 FIX: Pass duplicates in the lookup list to test Generator's internal deduping
        code = gen.generate_script(lookups=['lookup.sav', 'lookup.sav'])
        
        # Expect the BODY to have 2 joins (Faithful Transpilation)
        assert code.count("left_join") == 2
        
        # Expect the SIGNATURE to have 1 argument (Safe Interface)
        # We check the count of the argument definition
        assert code.count("lookup = NULL") == 1