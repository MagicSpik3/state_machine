import re
from spss_engine.events import FileReadEvent

class DataLoaderParser:
    def parse(self, raw_command: str) -> FileReadEvent:
        cmd = raw_command.strip()
        
        # 1. Extract Filename
        file_match = re.search(r"(?:/| )FILE\s*=?\s*['\"](.*?)['\"]", cmd, re.IGNORECASE)
        if not file_match:
             if "GET FILE" in cmd.upper():
                 file_match = re.search(r"['\"](.*?)['\"]", cmd)
        
        filename = file_match.group(1) if file_match else "unknown_data"

        # 2. Extract Delimiter
        delim_match = re.search(r"/DELIMITERS\s*=\s*['\"](.*?)['\"]", cmd, re.IGNORECASE)
        is_sav = filename.lower().endswith(".sav")
        delimiter = delim_match.group(1) if delim_match else (None if is_sav else ",")
        
        if delimiter == "\\t": 
            delimiter = "\t"

        # 3. Check for Header
        header_row = False
        first_case_match = re.search(r"/FIRSTCASE\s*=\s*(\d+)", cmd, re.IGNORECASE)
        if first_case_match and int(first_case_match.group(1)) > 1:
            header_row = True

        # 4. Extract Variables
        variables = []
        # Strategy: Grab everything after /VARIABLES= until the end of the string
        # Then we let findall pick out the valid pairs, ignoring noise/newlines.
        var_start = re.search(r"/VARIABLES\s*=", cmd, re.IGNORECASE)
        
        if var_start:
            # Slice the string from the end of the match
            var_block = cmd[var_start.end():]
            
            # Remove the trailing command terminator (.) if it exists at the very end
            var_block = var_block.rstrip(".")
            
            # Regex: Name + Whitespace + Type (handling decimals like F8.2)
            # We trust findall to skip over newlines and spaces
            matches = re.findall(r"(\w+)\s+([A-Za-z]+\d+(?:\.\d+)?)", var_block)
            variables = matches

        return FileReadEvent(
            source_command=cmd,
            filename=filename,
            format="SAV" if is_sav else "TXT",
            delimiter=delimiter,
            header_row=header_row,
            variables=variables
        )