from spss_engine.state import StateMachine
try:
    import graphviz
except ImportError:
    graphviz = None

class GraphGenerator:
    """
    Converts the StateMachine's history ledger into a DOT (Graphviz) string.
    Visualizes the 'Time Machine' logic: how variables evolve.
    Also provides a render method.
    """

    @staticmethod
    def generate_dot(state_machine: StateMachine) -> str:
        lines = ["digraph StateMachine {", "    rankdir=LR;", "    node [shape=box fontname=\"Courier\"];"]
        
        # Iterate over every variable in the ledger
        for var_name, history in state_machine.history_ledger.items():
            
            previous_node_id = None
            
            for version in history:
                node_id = version.id
                
                # Escape quotes in source code for DOT format
                clean_source = version.source.replace('"', "'")
                
                # Create Node
                # AGE_0 [label="AGE_0\nCOMPUTE Age = 0."];
                label = f"{node_id}\\n{clean_source}"
                lines.append(f'    {node_id} [label="{label}"];')
                
                # Create Edge from previous version (if exists)
                if previous_node_id:
                    lines.append(f'    {previous_node_id} -> {node_id};')
                
                previous_node_id = node_id
                
        lines.append("}")
        return "\n".join(lines) 

    @staticmethod
    def render(state_machine: StateMachine, filename: str = "output", format: str = "png") -> str:
        """
        Renders the state machine to an image file.
        Returns the full path of the rendered file.
        """
        if graphviz is None:
            raise ImportError("The 'graphviz' library is required to render images. pip install graphviz")

        dot_source = GraphGenerator.generate_dot(state_machine)
        
        # graphviz.Source handles the temp file creation and system call to 'dot'
        src = graphviz.Source(dot_source)
        
        # render(filename, cleanup=True) will create filename.png and remove the temp .dot file
        output_path = src.render(filename=filename, format=format, cleanup=True)
        
        return output_path    