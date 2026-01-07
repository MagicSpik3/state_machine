import pytest
from spss_engine.state import StateMachine
from code_forge.generator import RGenerator

class TestGeneratorDataDiscovery:
    """
    Tests that the RGenerator can discover data dependencies (MATCH FILES)
    from the State Machine history.
    """

    def test_state_machine_join_discovery(self):
        # 1. Setup: State Machine with a registered System Join
        state = StateMachine()
        join_cmd = "MATCH FILES /TABLE='benefit_rates.sav' /BY rate_id."
        
        # We manually register the node, simulating the Pipeline's work
        state.register_assignment("###SYS_JOIN_1###", join_cmd, dependencies=[])
        
        # 2. Initialize Generator (No raw_source needed!)
        generator = RGenerator(state)
        
        # 3. Generate Script
        script = generator.generate_script()
        
        # 4. Assertions
        # A. Function Signature must include the discovered table
        assert "function(df, benefit_rates = NULL)" in script
        
        # B. Auto-loader must be present
        assert 'benefit_rates <- read_csv' in script
        
        # C. Join must be present
        assert "left_join(benefit_rates, by='rate_id')" in script

    def test_ignores_duplicates(self):
        """Ensure we don't generate duplicate arguments for the same table."""
        state = StateMachine()
        join_cmd = "MATCH FILES /TABLE='lookup.sav' /BY id."
        
        # Register two separate nodes with the same command
        state.register_assignment("###SYS_JOIN_1###", join_cmd, dependencies=[])
        state.register_assignment("###SYS_JOIN_2###", join_cmd, dependencies=[])
        
        generator = RGenerator(state)
        script = generator.generate_script()
        
        # Should only appear once in signature
        assert script.count("lookup = NULL") == 1