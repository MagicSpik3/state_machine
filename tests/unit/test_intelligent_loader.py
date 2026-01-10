import pytest
from spss_engine.parsers.data_loader import DataLoaderParser

class TestIntelligentLoader:
    def test_parse_complex_get_data(self):
        raw_cmd = """
        GET DATA
        /TYPE=TXT
        /FILE='input_people.csv'
        /DELCASE=LINE
        /DELIMITERS=','
        /QUALIFIER='"'
        /ARRANGEMENT=DELIMITED
        /FIRSTCASE=2
        /VARIABLES=
          id F8.0
          age F8.0
          gender A1
          income F10.0
        .
        """
        
        parser = DataLoaderParser()
        event = parser.parse(raw_cmd)
        
        # Verify File Details
        assert event.filename == "input_people.csv"
        assert event.delimiter == ","
        assert event.qualifier == '"'
        assert event.header_row is True
        
        # Verify Schema Extraction
        assert len(event.variables) == 4
        assert event.variables[0] == ("id", "F8.0")
        assert event.variables[2] == ("gender", "A1")