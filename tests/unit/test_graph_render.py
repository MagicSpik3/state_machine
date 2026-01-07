import pytest
from unittest.mock import MagicMock, patch
from spss_engine.state import StateMachine
from spec_writer.graph import GraphGenerator

class TestGraphRender:
    """
    Strictly verifies the API contract of GraphGenerator.render.
    """
    
    def test_render_signature_compliance(self):
        """
        Verify that calling render with 'filename' (Old API) raises a TypeError.
        This ensures we have fixed the definition in graph.py.
        """
        state = StateMachine()
        generator = GraphGenerator(state)
        
        # We Mock the internal generate_dot to avoid needing graphviz installed
        with patch.object(generator, 'generate_dot', return_value="digraph {}"):
            with patch('graphviz.Source') as mock_source:
                # 1. Test expected failure (Old API)
                with pytest.raises(TypeError) as exc:
                    generator.render(filename="wrong_arg")
                assert "unexpected keyword argument 'filename'" in str(exc.value)

                # 2. Test expected success (New API)
                # We mock the render output to avoid file IO
                mock_source.return_value.render.return_value = "output.png"
                
                result = generator.render("correct_path")
                assert result == "output.png"