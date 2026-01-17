import pytest
from spss_engine.parsers.data_loader import DataLoaderParser
from spss_engine.events import FileReadEvent

class TestDataLoaderParser:
    """
    Verifies that the parser correctly extracts metadata (schema info)
    from raw SPSS GET DATA commands.
    """
    
    def setup_method(self):
        self.parser = DataLoaderParser()

    def test_parse_simple_csv(self):
        """
        Scenario: Standard CSV load with variables.
        """
        raw = """
        GET DATA
          /TYPE=TXT
          /FILE="input_people.csv"
          /DELCASE=LINE
          /DELIMITERS=","
          /ARRANGEMENT=DELIMITED
          /FIRSTCASE=2
          /VARIABLES=
            id F8.0
            name A20
            joined_date ADATE10.
        """
        
        event = self.parser.parse(raw)
        
        assert isinstance(event, FileReadEvent)
        assert event.filename == "input_people.csv"
        assert event.delimiter == ","
        assert event.header_row is True # FIRSTCASE=2 implies header at 1
        
        # Verify Variable Extraction
        assert len(event.variables) == 3
        assert event.variables[0] == ("id", "F8.0")
        assert event.variables[1] == ("name", "A20")
        assert event.variables[2] == ("joined_date", "ADATE10")

    def test_parse_sav_file(self):
        """
        Scenario: GET FILE (Binary SAV) has no variables listed usually.
        """
        raw = "GET FILE='dataset.sav'."
        
        event = self.parser.parse(raw)
        
        assert event.filename == "dataset.sav"
        # SAV files don't have delimiters or variable lists in the GET command
        assert event.delimiter is None
        assert event.variables == []

    def test_parse_tab_delimiter(self):
        """
        Scenario: Tab delimited file (\t).
        """
        raw = 'GET DATA /FILE="data.txt" /DELIMITERS="\\t" /VARIABLES= x F1.0.'
        
        event = self.parser.parse(raw)
        # 🟢 CHANGED: Expect the resolved tab character, not the escaped string
        assert event.delimiter == "\t" 
        assert event.filename == "data.txt"
        assert event.variables == [("x", "F1.0")]
