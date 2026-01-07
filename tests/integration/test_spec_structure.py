import pytest
import os
from unittest.mock import MagicMock
from spss_engine.pipeline import CompilerPipeline
from spec_writer.conductor import Conductor
from spec_writer.describer import SpecGenerator

class MockLLM:
    """
    Mocks the OllamaClient to avoid real AI calls during testing.
    Returns deterministic titles/descriptions based on the prompt.
    """
    def generate(self, prompt: str) -> str:
        # Normalize for case-insensitive matching
        p_lower = prompt.lower()
        
        # 1. Title Generation
        # SpecGenerator usually asks for a "Title" or "Summary"
        if "title" in p_lower:
            if "min_age_n" in p_lower: return "Control Variable: Minimum Age"
            if "benefit_type" in p_lower: return "Benefit Rate Loading"
            if "payment_amount" in p_lower: return "Calculate Payment"
            return "Logic Cluster"
            
        # 2. Description Generation
        # SpecGenerator usually asks to "Describe" or "Explain"
        if "explain" in p_lower or "describe" in p_lower:
            if "min_age_n" in p_lower: return "Calculates the minimum age threshold."
            return "The logic calculates the target variable based on inputs."
            
        return "Generated Text"

class TestSpecStructure:
    """
    Ensures that the Spec Generator correctly identifies structural boundaries
    and produces a readable Markdown specification.
    """

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
        # 1. Compile
        pipeline = CompilerPipeline()
        pipeline.process(legacy_code)
        
        # 2. Analyze
        conductor = Conductor(pipeline.state_machine)
        clusters = conductor.identify_clusters()
        
        # 3. Structural Assertions
        assert len(clusters) >= 2, "Logic should be fragmented into clusters"
        
        min_age_cluster = None
        payment_cluster = None
        
        for i, cluster in enumerate(clusters):
            for node_id in cluster:
                # Note: node_id might be uppercase like MIN_AGE_N_0
                if "MIN_AGE_N" in node_id: min_age_cluster = i
                if "PAYMENT_AMOUNT" in node_id: payment_cluster = i
                    
        assert min_age_cluster is not None
        assert payment_cluster is not None
        assert min_age_cluster != payment_cluster, "ETL Logic leaked into Main Pipeline"

    def test_generate_and_save_spec(self, legacy_code):
        """
        Runs the full SpecGenerator with a Mock LLM and saves the output.
        """
        # 1. Setup
        pipeline = CompilerPipeline()
        pipeline.process(legacy_code)
        
        # 2. Initialize Generator with Mock LLM
        mock_ai = MockLLM()
        generator = SpecGenerator(pipeline.state_machine, mock_ai)
        
        # 3. Generate Report
        spec_content = generator.generate_report(dead_ids=[], runtime_values={})
        
        # 4. Save Artifact for User Review
        output_dir = "tests/integration"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "generated_spec_structure.md")
        
        with open(output_path, "w") as f:
            f.write(spec_content)
            
        print(f"\n✅ Spec saved to: {os.path.abspath(output_path)}")
        
        # 5. Verification
        # Check that our "Chapters" (Clusters) appear in the text
        assert "Control Variable: Minimum Age" in spec_content, \
            f"Spec content missing expected title. Got:\n{spec_content}"
        assert "Calculate Payment" in spec_content
        
        # Check that the file actually exists
        assert os.path.exists(output_path)
        