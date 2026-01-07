import pytest
from spss_engine.state import StateMachine
from spec_writer.graph import GraphGenerator

class TestGraphGenerator:
    def test_single_variable_lifecycle(self):
        """
        Test that a single variable's history produces a linear chain of nodes.
        AGE_0 -> AGE_1
        """
        # 1. Setup State manually
        state = StateMachine()
        state.register_assignment("Age", "COMPUTE Age = 0.", dependencies=[])
        state.register_assignment("Age", "COMPUTE Age = 25.", dependencies=["Age_0"]) # Link dep explicitly for graph test
        
        # 2. Generate DOT (FIX: Instantiate class)
        generator = GraphGenerator(state)
        dot_output = generator.generate_dot()
        
        assert "AGE_0" in dot_output
        assert "AGE_1" in dot_output
        assert "AGE_0 -> AGE_1" in dot_output

    def test_multi_variable_graph(self):
        """
        Test that multiple independent variables create disjoint subgraphs.
        """
        state = StateMachine()
        state.register_assignment("x", "x=1", dependencies=[])
        state.register_assignment("y", "y=2", dependencies=[])
        
        # FIX: Instantiate class
        generator = GraphGenerator(state)
        dot = generator.generate_dot()
        
        assert "X_0" in dot
        assert "Y_0" in dot
        # They should not be connected
        assert "X_0 -> Y_0" not in dot

    def test_dead_code_highlighting(self):
        """
        Test that dead nodes are rendered with a specific color (Red).
        """
        state = StateMachine()
        state.register_assignment("x", "x=1", dependencies=[])
        state.register_assignment("x", "x=2", dependencies=["X_0"])
        
        dead_ids = ["X_0"]
        
        # FIX: Instantiate class and pass argument
        generator = GraphGenerator(state)
        dot = generator.generate_dot(highlight_dead=dead_ids)
        
        # Check for red styling on the dead node
        assert 'X_0 [label="X_0\\nx=1" color="red" fontcolor="red" style="dashed"];' in dot
        # Live node should not have red styling (or at least not the full string match)
        assert 'color="red"' in dot # At least one node is red