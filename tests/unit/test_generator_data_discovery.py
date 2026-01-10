import pytest
from spss_engine.state import StateMachine
from code_forge.generator import RGenerator

class TestGeneratorDataDiscovery:
    
    def test_signature_generation_with_lookups(self):
        """
        Verify that IF lookups are passed, they appear in the signature.
        """
        state = StateMachine()
        # Add a dummy node so it's not "empty logic"
        state.register_assignment("X", "COMPUTE X=1.", [])
        
        generator = RGenerator(state)
        
        # Explicitly pass the lookups (simulating Orchestrator passing Inspector results)
        lookups = ["benefit_rates.sav", "zip_codes.csv"]
        
        script = generator.generate_script(lookups=lookups)
        
        # Assertions
        assert "function(df, benefit_rates = NULL, zip_codes = NULL)" in script
        assert "#' @param benefit_rates" in script
        assert "#' @param zip_codes" in script