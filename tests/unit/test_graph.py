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
        state.register_assignment("Age", "COMPUTE Age = 0.")
        state.register_assignment("Age", "COMPUTE Age = 25.")

        # 2. Generate DOT
        dot_output = GraphGenerator.generate_dot(state)

        # 3. Assertions
        # Check Nodes exist
        assert "AGE_0" in dot_output
        assert "AGE_1" in dot_output

        # Check Edges exist (Sequence)
        assert "AGE_0 -> AGE_1" in dot_output

        # --- FIX IS HERE ---
        # The label includes the Node ID and a newline (\n)
        assert 'label="AGE_0\\nCOMPUTE Age = 0."' in dot_output
        assert 'label="AGE_1\\nCOMPUTE Age = 25."' in dot_output

    def test_multi_variable_graph(self):
        """
        Test that multiple independent variables create disjoint subgraphs.
        """
        state = StateMachine()
        state.register_assignment("x", "x=1")
        state.register_assignment("y", "y=2")

        dot = GraphGenerator.generate_dot(state)

        assert "X_0" in dot
        assert "Y_0" in dot
        # There should be NO edge between X and Y
        assert "X_0 -> Y_0" not in dot

    def test_dead_code_highlighting(self):
        """
        Test that dead nodes are rendered with a specific color (Red).
        """
        state = StateMachine()
        state.register_assignment("x", "x=1")  # X_0 (Dead)
        state.register_assignment("x", "x=2")  # X_1 (Live)

        # We manually tell the generator that X_0 is dead
        dead_ids = ["X_0"]

        dot = GraphGenerator.generate_dot(state, highlight_dead=dead_ids)

        # X_0 should be red
        assert 'X_0 [label="X_0\\nx=1" style=filled fillcolor="#ffcccc"];' in dot

        # X_1 should be standard (no fillcolor)
        assert 'X_1 [label="X_1\\nx=2"];' in dot
