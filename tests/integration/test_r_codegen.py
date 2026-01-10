import pytest
from spss_engine.events import FileReadEvent
from code_forge.generator import RGenerator

class TestRCodegen:
    def test_generate_strict_loader(self):
        # 1. Create a Rich Event (simulating what Parser produces)
        event = FileReadEvent(
            source_command="raw",
            filename="input_people.csv",
            delimiter=",",
            qualifier='"',
            header_row=True,
            variables=[
                ("id", "F8.0"),
                ("age", "F8.0"),
                ("gender", "A1"),
                ("income", "F10.0")
            ]
        )
        
        # 2. Generate Code
        # We pass None for state_machine as we are testing the static generator method
        gen = RGenerator(state_machine=None) 
        code = gen.generate_standalone_script([event])
        
        # 3. Assertions (Matching your Definition of Done)
        assert 'df <- read.csv(' in code
        assert 'sep = ","' in code
        assert 'quote = "\\""' in code # Escaped quote
        assert 'stringsAsFactors = FALSE' in code
        
        assert 'df$id <- as.numeric(df$id)' in code
        assert 'df$gender <- as.character(df$gender)' in code