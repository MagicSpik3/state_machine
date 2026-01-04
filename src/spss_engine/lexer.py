import re
from typing import List

class SpssLexer:
    """
    Responsible for reading raw SPSS syntax text and splitting it into 
    discrete commands, handling '.' termination and quote balancing.
    """

    def __init__(self, raw_text: str):
        self.raw_text = raw_text

    def get_commands(self) -> List[str]:
        """
        Splits the raw text into a list of cleaned command strings.
        """
        commands = []
        current_command = []
        in_quote = False
        quote_char = None
        
        # We iterate character by character or line by line?
        # Line by line is safer for memory, but character is safer for parsing.
        # Let's stick to line-based but add quote tracking.
        
        lines = self.raw_text.splitlines()
        
        for line in lines:
            stripped_line = line.strip()
            
            if not stripped_line:
                continue
            
            # Aggregate the line
            current_command.append(line)
            
            # Update quote state for this line
            # This is a naive toggle. It works for simple cases.
            # Escaped quotes (e.g., 'Don''t') are tricky in SPSS (doubled quotes).
            for char in line:
                if char in ('"', "'"):
                    if not in_quote:
                        in_quote = True
                        quote_char = char
                    elif char == quote_char:
                        in_quote = False
                        quote_char = None
            
            # A command ends if:
            # 1. The line ends with a dot.
            # 2. We are NOT currently inside an open quote string.
            if stripped_line.endswith('.') and not in_quote:
                full_cmd = "\n".join(current_command)
                commands.append(full_cmd)
                current_command = []
        
        # Catch residuals
        if current_command:
            commands.append("\n".join(current_command))
            
        return commands

    def normalize_command(self, command: str) -> str:
        """
        Cleans up a command string:
        - Removes extra whitespace
        """
        # Improved regex to handle basic whitespace without stripping quotes logic
        return re.sub(r'\s+', ' ', command).strip()