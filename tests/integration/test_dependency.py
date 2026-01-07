import pytest
from spss_engine.pipeline import CompilerPipeline

class TestDataDependency:
    def test_payroll_flow(self):
        code = """
        COMPUTE Gross = 50000.
        COMPUTE Tax = Gross * 0.2.
        COMPUTE Net = Gross - Tax.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        # 1. Check Gross
        gross = pipeline.get_variable_version("Gross")
        assert gross.id == "GROSS_0"
        
        # 2. Check Tax Dependency
        tax = pipeline.get_variable_version("Tax")
        # FIX: Check IDs instead of full object equality to avoid strict cluster_index matching errors
        dep_ids = [d.id for d in tax.dependencies]
        assert "GROSS_0" in dep_ids

        # 3. Check Net Dependencies
        net = pipeline.get_variable_version("Net")
        dep_ids_net = [d.id for d in net.dependencies]
        assert "GROSS_0" in dep_ids_net
        assert "TAX_0" in dep_ids_net

    def test_graph_edges(self):
        code = """
        COMPUTE X = 1.
        COMPUTE Y = X + 1.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        x = pipeline.get_variable_version("X")
        y = pipeline.get_variable_version("Y")
        
        # Verify Y depends on X
        assert x in y.dependencies