# 2. Dependency Edges (Data Flow) - NEW
# We need to find the "Latest Version" of the dependent variable
# that existed *before* this node.
# This is complex. For now, let's just point to the *Current* version of that dependency
# stored in the state machine?
# Actually, for a visual graph, identifying the specific version node is hard without a lookup.
#
# SIMPLIFICATION: just try to link to the 'most recent' version of that dependency?
# Or, better: StateMachine should allow us to look up "What was the version of X when this line ran?"
#
# For this step, let's just render the edge if we can guess the node ID.
# We will simply look up the current max version of that dependency?
# No, that's wrong (time travel).
try:
    import graphviz
except ImportError:
    graphviz = None
from typing import List, Optional
from spss_engine.state import StateMachine


class GraphGenerator:
    """
    Converts the StateMachine's history ledger into a DOT (Graphviz) string
    and handles image rendering.
    """

    @staticmethod
    def generate_dot(
        state_machine: StateMachine, highlight_dead: List[str] = None
    ) -> str:
        if highlight_dead is None:
            highlight_dead = []

        lines = [
            "digraph StateMachine {",
            "    rankdir=LR;",
            '    node [shape=box fontname="Courier"];',
        ]

        for var_name, history in state_machine.history_ledger.items():
            previous_node_id = None

            for version in history:
                node_id = version.id
                clean_source = version.source.replace('"', "'")

                # Determine Style
                style_attr = ""
                if node_id in highlight_dead:
                    # Paint it Red
                    style_attr = ' style=filled fillcolor="#ffcccc"'

                label = f"{node_id}\\n{clean_source}"
                lines.append(f'    {node_id} [label="{label}"{style_attr}];')

                # 1. Sequence Edge
                if previous_node_id:
                    lines.append(f"    {previous_node_id} -> {node_id} [weight=2];")

                # 2. Dependency Edges
                for dep_id in version.dependencies:
                    lines.append(
                        f"    {dep_id} -> {node_id} [style=dashed constraint=false color=blue];"
                    )

                previous_node_id = node_id

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def render(
        state_machine: StateMachine,
        filename: str = "output",
        format: str = "png",
        highlight_dead: List[str] = None,
    ) -> str:
        """
        Renders the state machine to an image file.
        Returns the full path of the rendered file.
        """
        if graphviz is None:
            raise ImportError(
                "The 'graphviz' library is required. pip install graphviz"
            )

        dot_source = GraphGenerator.generate_dot(
            state_machine, highlight_dead=highlight_dead
        )

        src = graphviz.Source(dot_source)

        # render(filename, cleanup=True) will create filename.png and remove the temp .dot file
        output_path = src.render(filename=filename, format=format, cleanup=True)

        return output_path
