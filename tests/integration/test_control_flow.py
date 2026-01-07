import pytest
from spss_engine.pipeline import CompilerPipeline

class TestControlFlow:
    """
    Verifies that control flow structures (DO IF, EXECUTE) are parsed 
    and represented in the graph (even if abstractly).
    """
    def test_flag_variable_nightmare(self):
        """
        Scenario: A flag is toggled multiple times inside conditionals.
        """
        code = """
        COMPUTE x = 0.
        DO IF (x = 0).
          COMPUTE x = 1.
        END IF.
        DO IF (x = 1).
          COMPUTE x = 2.
        END IF.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)
        
        x_history = pipeline.get_variable_history("x")
        
        # Expectation: 3 versions (X_0=0, X_1=1, X_2=2)
        assert len(x_history) == 3
        
        # FIX: Extract IDs for comparison
        ids = [v.id for v in x_history]
        assert "X_0" in ids
        assert "X_1" in ids
        assert "X_2" in ids
        
        # Verify strict order
        assert x_history[0].version == 0
        assert x_history[2].version == 2