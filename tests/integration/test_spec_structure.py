import pytest
import os
from unittest.mock import MagicMock
from spss_engine.pipeline import CompilerPipeline
from spec_writer.conductor import Conductor
from spec_writer.describer import SpecGenerator

class MockLLM:
    """
    Mocks the OllamaClient to avoid real AI calls during testing.
    """
    def generate(self, prompt: str) -> str:
        p_lower = prompt.lower()
        
        # 1. Title Generation
        if "title" in p_lower:
            # FIX: Check for 'payment' FIRST because it's the high-value business output.
            # 'benefit_type' is just a join key that appears in the same cluster.
            if "payment" in p_lower or "pay" in p_lower: 
                return "Calculate Payment"
                
            if "min_age_n" in p_lower: 
                return "Control Variable: Minimum Age"
                
            if "benefit_type" in p_lower: 
                return "Benefit Rate Loading"
                
            return "Logic Cluster"
            
        # 2. Description Generation
        if "explain" in p_lower or "describe" in p_lower:
            if "min_age_n" in p_lower: return "Calculates the minimum age threshold."
            return "The logic calculates the target variable based on inputs."
            
        return "Generated Text"

class TestSpecStructure:
    # ... (Keep existing fixture and test_identify_distinct_processing_phases) ...
    @pytest.fixture
    def legacy_code(self):
        return """
        * STEP 0a: Control Vars.
        GET DATA /FILE='control_vars.csv'.
        COMPUTE min_age_n = NUMBER(value, F3.0).
        SELECT IF NOT MISSING(min_age_n).
        SAVE OUTFILE='control_values.sav'.

        * STEP 0b: Benefit Rates.
        GET DATA /FILE='benefit_rates.csv'.
        SORT CASES BY benefit_type.
        SAVE OUTFILE='benefit_rates.sav'.

        * STEP 1: Main Logic.
        GET DATA /FILE='claims_data.csv'.
        MATCH FILES /FILE=* /TABLE='control_values.sav' /BY join_key.
        MATCH FILES /FILE=* /TABLE='benefit_rates.sav' /BY benefit_type.
        
        COMPUTE payment_amount = eligible_days * daily_rate.
        SAVE TRANSLATE /OUTFILE='benefit_monthly_summary.csv'.
        """

    def test_identify_distinct_processing_phases(self, legacy_code):
        pipeline = CompilerPipeline()
        pipeline.process(legacy_code)
        conductor = Conductor(pipeline.state_machine)
        clusters = conductor.identify_clusters()
        non_empty = [c for c in clusters if len(c) > 0]
        assert len(non_empty) >= 2, f"Logic should be fragmented, found {len(non_empty)}"

    def test_generate_and_save_spec(self, legacy_code):
        """
        Runs the full SpecGenerator with a Mock LLM and saves the output.
        """
        pipeline = CompilerPipeline()
        pipeline.process(legacy_code)
        
        mock_ai = MockLLM()
        generator = SpecGenerator(pipeline.state_machine, mock_ai)
        spec_content = generator.generate_report(dead_ids=[], runtime_values={})
        
        output_dir = "tests/integration"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "generated_spec_structure.md")
        
        with open(output_path, "w") as f:
            f.write(spec_content)
            
        print(f"\n✅ Spec saved to: {os.path.abspath(output_path)}")
        
        # Verification
        assert "Control Variable: Minimum Age" in spec_content
        assert "Calculate Payment" in spec_content