from spss_engine.state import StateMachine, VariableVersion
from typing import List, Optional
import graphviz
import os
import logging

logger = logging.getLogger("GraphGenerator")

class GraphGenerator:
    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine

    def _sanitize_label(self, label: str) -> str:
        return label.replace('"', '\\"').replace('\n', '\\n')

    def generate_dot(self, highlight_dead: List[str] = None) -> str:
        """
        Generates the DOT source code for the state machine.
        """
        if highlight_dead is None: highlight_dead = []
        
        dot = ["digraph StateMachine {"]
        dot.append('    rankdir=LR;')
        dot.append('    node [shape=box fontname="Courier"];')

        # 1. Define Nodes
        for node in self.state_machine.nodes:
            label = f"{node.id}\\n{self._sanitize_label(node.source)}"
            
            style_attrs = ""
            if node.id in highlight_dead:
                style_attrs = ' color="red" fontcolor="red" style="dashed"'
            
            dot.append(f'    {node.id} [label="{label}"{style_attrs}];')

        # 2. Define Edges
        for node in self.state_machine.nodes:
            for dep in node.dependencies:
                # Handle Case Sensitivity and Object vs String
                if isinstance(dep, VariableVersion):
                    dep_id = dep.id
                else:
                    dep_id = str(dep).upper()
                
                edge_style = "dashed constraint=false color=blue"
                if node.id in highlight_dead or dep_id in highlight_dead:
                    edge_style = "dotted constraint=false color=red"

                dot.append(f'    {dep_id} -> {node.id} [style={edge_style}];')

        dot.append("}")
        return "\n".join(dot)

    def render(self, output_path: str):
        """
        Renders the graph to a PNG file.
        Arguments:
            output_path: The full path (without extension) or base filename.
        """
        try:
            dot_source = self.generate_dot()
            src = graphviz.Source(dot_source, format='png')
            
            # Renders to {output_path}.png
            output_file = src.render(filename=output_path, cleanup=True)
            logger.info(f"Graph rendered to {output_file}")
            return output_file
        except Exception as e:
            logger.debug(f"Failed DOT Source:\n{self.generate_dot()}")
            raise e