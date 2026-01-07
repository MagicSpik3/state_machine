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
    def _sanitize_label(text: str) -> str:
        """
        Escapes characters that break Graphviz DOT string literals.
        """
        if not text:
            return ""
        # 1. Escape backslashes first (so we don't double-escape later)
        text = text.replace("\\", "\\\\")
        # 2. Escape double quotes
        text = text.replace('"', '\\"')
        # 3. Collapse real newlines into literal "\n" characters
        text = text.replace("\n", "\\n")
        return text

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
                
                # FIX: Use robust sanitization instead of naive replace
                clean_source = GraphGenerator._sanitize_label(version.source)

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
        # We catch exceptions here to provide better error messages
        try:
            output_path = src.render(filename=filename, format=format, cleanup=True)
            return output_path
        except Exception as e:
            # If rendering fails, dump the source for debugging
            print(f"DEBUG: Failed DOT Source:\n{dot_source}")
            raise e