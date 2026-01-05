import pytest
from spss_engine.pipeline import CompilerPipeline
from spss_engine.graph import GraphGenerator


class TestDataDependency:

    def test_payroll_flow(self):
        """
        Scenario: Calculating Net Pay.
        Flow: Gross -> Tax -> Net.

        We want to ensure the graph records that Net_Pay depends on Gross and Tax.
        """
        code = """
        * Init.
        COMPUTE Gross = 50000.
        COMPUTE Rate = 0.2.
        
        * Calculate Tax (Depends on Gross, Rate).
        COMPUTE Tax = Gross * Rate.
        
        * Calculate Net (Depends on Gross, Tax).
        COMPUTE Net = Gross - Tax.
        """

        pipeline = CompilerPipeline()
        pipeline.process(code)

        # 1. Inspect the State of 'Net'
        history = pipeline.get_variable_history("Net")
        assert len(history) == 1
        net_version = history[0]

        # 2. Check Dependencies
        # THE FIX: We now expect fully resolved SSA IDs (GROSS_0, TAX_0)
        # because the pipeline looked up the current version at that moment.
        assert "GROSS_0" in net_version.dependencies
        assert "TAX_0" in net_version.dependencies

    def test_graph_edges(self):
        """
        Verify that the generated DOT file contains dashed edges for dependencies.
        """
        code = """
        COMPUTE x = 10.
        COMPUTE y = x + 5.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)

        # Generate the graph source
        dot = GraphGenerator.generate_dot(pipeline.state_machine)

        # Check for the dashed dependency line: x_0 -> y_0
        # "X_0 -> Y_0 [style=dashed ...]"
        assert "X_0 -> Y_0" in dot
        assert "style=dashed" in dot
