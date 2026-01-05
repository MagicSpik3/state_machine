import pytest
from spss_engine.pipeline import CompilerPipeline


class TestDeadCodeAnalysis:

    def test_level_1_simple_overwrite(self):
        """
        Level 1: Direct Overwrite.
        'x' is set to 1, then immediately set to 2.
        Version X_0 was never used. It is dead.
        """
        code = """
        COMPUTE x = 1.
        COMPUTE x = 2.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)

        dead_vars = pipeline.analyze_dead_code()

        assert "X_0" in dead_vars
        assert "X_1" not in dead_vars  # Final version is always live

    def test_level_2_read_before_write(self):
        """
        Level 2: Usage Saves the Life.
        'x' is set to 1, USED by 'y', then set to 2.
        X_0 is overwritten, BUT it was used. It must be LIVE.
        """
        code = """
        COMPUTE x = 1.
        COMPUTE y = x + 5.
        COMPUTE x = 2.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)

        dead_vars = pipeline.analyze_dead_code()

        assert "X_0" not in dead_vars  # It was used by Y_0
        assert "X_1" not in dead_vars  # It is the final state
        assert "Y_0" not in dead_vars  # It is the final state of Y

    def test_level_3_transient_variable(self):
        """
        Level 3: The Intermediate Zombie.
        'temp' is created, used to calculate 'x', then overwritten.
        Wait... if 'temp' is used, it's live.

        Let's try a different one:
        A variable 'temp' is set, then 'temp' is set again without anyone reading the first one.
        AND another variable 'z' is set but overwritten.
        """
        code = """
        COMPUTE temp = 100.
        COMPUTE temp = 200. 
        COMPUTE final = temp + 5.
        """
        pipeline = CompilerPipeline()
        pipeline.process(code)

        dead_vars = pipeline.analyze_dead_code()

        # TEMP_0 (100) was never used. Dead.
        assert "TEMP_0" in dead_vars

        # TEMP_1 (200) was used by final. Live.
        assert "TEMP_1" not in dead_vars
