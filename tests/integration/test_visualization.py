import os
import pytest
from spss_engine.state import StateMachine
from spec_writer.graph import GraphGenerator

# Skip if graphviz is not installed to avoid breaking CI environments
try:
    import graphviz

    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False


@pytest.mark.skipif(not HAS_GRAPHVIZ, reason="Graphviz library not installed")
class TestVisualization:

    def test_render_png_file(self, tmp_path):
        """
        Integration: Create a state, generate DOT, and render to PNG.
        """
        # 1. Setup State
        state = StateMachine()
        state.register_assignment("Age", "COMPUTE Age = 25.")
        state.register_assignment("Age", "IF (x) COMPUTE Age = 26.")

        # 2. Define Output Path in temp dir
        output_file = tmp_path / "logic_flow"

        # 3. Call the Render method (We need to implement this!)
        output_path = GraphGenerator.render(
            state, filename=str(output_file), format="png"
        )

        # 4. Verify the file exists
        # Graphviz usually appends the extension, so logic_flow.png
        expected_file = str(output_file) + ".png"

        assert os.path.exists(expected_file)
        assert os.path.getsize(expected_file) > 0
