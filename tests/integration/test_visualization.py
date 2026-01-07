import pytest
import os
from spss_engine.state import StateMachine
from spec_writer.graph import GraphGenerator

class TestVisualization:
    
    def test_render_png_file(self, tmp_path):
        """
        Integration: Create a state, generate DOT, and render to PNG.
        """
        # 1. Setup State
        state = StateMachine()
        state.register_assignment("Age", "COMPUTE Age = 25.", dependencies=[])
        state.register_assignment("Age", "IF (x) COMPUTE Age = 26.", dependencies=["AGE_0"])
        
        # 2. Define Output Path in temp dir
        # Note: Graphviz appends the extension automatically, so we provide the base name
        output_base = tmp_path / "logic_flow"
        
        # 3. Call the Render method
        # FIX: Instantiate the class first
        generator = GraphGenerator(state)
        
        # FIX: Call instance method with simple signature (output_path)
        # format is hardcoded to 'png' in the current implementation
        output_path = generator.render(str(output_base))
        
        # 4. Verify
        # Graphviz returns the path to the generated file (with extension)
        assert output_path.endswith(".png")
        assert os.path.exists(output_path)