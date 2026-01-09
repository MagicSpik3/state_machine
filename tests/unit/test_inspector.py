import pytest
from spss_engine.inspector import SourceInspector

class TestSourceInspector:
    
    def test_finds_input_files(self):
        code = """
        GET DATA /TYPE=TXT /FILE='raw_data.csv'.
        MATCH FILES /FILE="lookup_table.sav".
        """
        inspector = SourceInspector()
        inputs, outputs = inspector.scan(code)
        
        assert "raw_data.csv" in inputs
        assert "lookup_table.sav" in inputs
        assert len(outputs) == 0

    def test_finds_output_files(self):
        code = """
        * Analysis. 
        FREQUENCIES variables=x.
        
        * Export Gold Standard.
        SAVE TRANSLATE
         /OUTFILE='gold_output.csv'
         /TYPE=CSV
         /REPLACE.
         
        * Also save binary.
        SAVE OUTFILE='final_data.sav'.
        """
        inspector = SourceInspector()
        inputs, outputs = inspector.scan(code)
        
        assert "gold_output.csv" in outputs
        assert "final_data.sav" in outputs
        assert len(inputs) == 0
        
    def test_ignores_false_positives(self):
        code = """
        * This comment talks about /FILE='ignore_me.csv'.
        GET DATA /FILE='real_data.csv'.
        """
        inspector = SourceInspector()
        inputs, outputs = inspector.scan(code)
        
        assert "real_data.csv" in inputs
        assert "ignore_me.csv" not in inputs