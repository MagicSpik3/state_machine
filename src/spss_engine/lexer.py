import re
from typing import List

class SpssLexer:
    """
    Responsible for reading raw SPSS syntax text and splitting it into
    discrete commands, handling '.' termination and quote balancing.
    """

    def __init__(self, raw_text: str = None):
        # Allow optional raw_text for backward compatibility
        self.raw_text = raw_text

    def split_commands(self, text: str = None) -> List[str]:
        """
        Splits the provided text (or self.raw_text) into cleaned command strings.
        This is the main stateless entry point.
        """
        target_text = text if text is not None else self.raw_text
        if target_text is None:
            raise ValueError("No text provided to split_commands")

        commands = []
        current_command = []
        in_quote = False
        quote_char = None

        lines = target_text.splitlines()

        for line in lines:
            stripped_line = line.strip()

            if not stripped_line:
                continue

            # Aggregate the line
            current_command.append(line)

            # Update quote state for this line
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
            if stripped_line.endswith(".") and not in_quote:
                full_cmd = "\n".join(current_command)
                commands.append(full_cmd)
                current_command = []

        # Catch residuals
        if current_command:
            commands.append("\n".join(current_command))

        return commands

    # Legacy alias to keep old code working if it calls get_commands()
    def get_commands(self) -> List[str]:
        return self.split_commands()

    def normalize_command(self, command: str) -> str:
        """
        Cleans up a command string: Removes extra whitespace.
        """
        return re.sub(r"\s+", " ", command).strip()