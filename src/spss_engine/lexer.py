import re
from typing import List, Iterator

class SpssLexer:
    """
    Responsible for reading raw SPSS syntax text and splitting it into 
    discrete commands, handling the specific '.' termination logic.
    """

    def __init__(self, raw_text: str):
        self.raw_text = raw_text

    def get_commands(self) -> List[str]:
        """
        Splits the raw text into a list of cleaned command strings.
        """
        commands = []
        current_command = []
        
        # Split by newlines first to handle line-based logic
        lines = self.raw_text.splitlines()
        
        for line in lines:
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                continue
                
            # Check for comments (Line starting with * or COMMENT)
            # Note: This is a simplified check. SPSS comments are tricky.
            # Ideally, we handle them as commands or ignore them. 
            # For now, we accumulate them like code to preserve structure.
            
            current_command.append(line)
            
            # The Critical Logic: Check if line ends with a terminal dot.
            # A command ends if the last non-whitespace character is '.'
            if stripped_line.endswith('.'):
                # Join the accumulated lines into one command string
                full_cmd = "\n".join(current_command)
                commands.append(full_cmd)
                current_command = []
        
        # Catch any residual text (e.g. file didn't end with a dot)
        if current_command:
            commands.append("\n".join(current_command))
            
        return commands

    def normalize_command(self, command: str) -> str:
        """
        Cleans up a command string:
        - Removes extra whitespace
        - Collapses newlines into spaces (optional, for regex parsing)
        """
        # Remove the trailing dot for easier parsing later? 
        # For now, let's keep it but strip surrounding whitespace.
        return re.sub(r'\s+', ' ', command).strip()