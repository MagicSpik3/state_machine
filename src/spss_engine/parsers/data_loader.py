import re
from spss_engine.events import FileReadEvent

class DataLoaderParser:
    def parse(self, raw_command: str) -> FileReadEvent:
        cmd = raw_command.strip()
        
        # 🟢 FIX: Added '?' to make slash optional.
        # Handles: GET DATA /FILE='x' AND GET FILE='x'
        file_match = re.search(r"/?FILE\s*=\s*(?:['\"]([^'\"]+)['\"]|([^\s/]+))", cmd, re.IGNORECASE)
        filename = file_match.group(1) if file_match and file_match.group(1) else (file_match.group(2) if file_match else "unknown")

        # 🟢 FIX: Added '?' here too for robustness
        delim_match = re.search(r"/?DELIMITERS\s*=\s*(['\"])(.*?)\1", cmd, re.IGNORECASE)
        delimiter = delim_match.group(2) if delim_match else ","
        if delimiter == "\\t": delimiter = "\t"

        qual_match = re.search(r"/?QUALIFIER\s*=\s*(['\"])(.*?)\1", cmd, re.IGNORECASE)
        qualifier = qual_match.group(2) if qual_match else '"'

        first_case_match = re.search(r"/?FIRSTCASE\s*=\s*(\d+)", cmd, re.IGNORECASE)
        first_case = int(first_case_match.group(1)) if first_case_match else 1
        has_header = (first_case > 1)

        # Variables block logic (kept from previous fix)
        variables = []
        var_block_match = re.search(r"/?VARIABLES\s*=\s*(.*)$", cmd, re.IGNORECASE | re.DOTALL)
        
        if var_block_match:
            block = var_block_match.group(1).strip()
            if block.endswith('.'):
                block = block[:-1]
                
            schema_pattern = re.compile(r"^\s*([A-Za-z0-9_]+)\s+([A-Z]\d+(?:\.\d+)?)", re.MULTILINE)
            variables = schema_pattern.findall(block)

        return FileReadEvent(
            source_command=cmd,
            filename=filename,
            format="TXT",
            delimiter=delimiter,
            qualifier=qualifier,
            header_row=has_header,
            skip_rows=0, 
            variables=variables
        )