import pytest
from spss_engine.state import StateMachine
from spss_engine.describer import SpecGenerator, MockLLM


class TestSpecGenerator:

    def test_live_code_filtering(self):
        """
        Ensure we DO NOT generate specs for Dead Code.
        """
        state = StateMachine()
        # Dead Variable (X_0)
        state.register_assignment("x", "x=1")
        # Live Variable (X_1)
        state.register_assignment("x", "x=2")

        # We need to manually mark X_0 as dead for this unit test
        # (In integration, the pipeline does this, but here we can just pass the list)
        dead_ids = ["X_0"]

        # Initialize Generator with a Mock LLM
        llm = MockLLM()
        generator = SpecGenerator(state, llm)

        # Generate Spec
        spec = generator.generate_report(dead_ids=dead_ids)

        # Assertions
        assert "X_0" not in spec
        assert "X_1" in spec

    def test_prompt_formatting(self):
        """
        Verify the prompt contains the provenance and dependencies.
        """
        state = StateMachine()
        state.register_assignment(
            "Net", "Net = Gross - Tax", dependencies=["GROSS_0", "TAX_0"]
        )

        llm = MockLLM()
        generator = SpecGenerator(state, llm)

        report = generator.generate_report()

        # The MockLLM just echoes the prompt, so we can check if the prompt had the right data
        assert "Net = Gross - Tax" in report
        assert "GROSS_0" in report
        assert "TAX_0" in report
