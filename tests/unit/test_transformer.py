import pytest
from spss_engine.transformer import CommandTransformer
from spss_engine.parser import ParsedCommand, TokenType
from spss_engine.events import (
    FileReadEvent, FileMatchEvent, FileSaveEvent, 
    AssignmentEvent, ScopeResetEvent
)

class TestCommandTransformer:
    
    @pytest.fixture
    def transformer(self):
        return CommandTransformer()

    def test_transform_file_read_destructive(self, transformer):
        """Scenario: GET DATA /FILE='data.csv'"""
        raw = "GET DATA /FILE='data.csv'."
        cmd = ParsedCommand(type=TokenType.FILE_READ, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 2
        assert isinstance(events[0], ScopeResetEvent)
        assert events[0].reason == "Destructive Load"
        assert isinstance(events[1], FileReadEvent)
        assert events[1].filename == "data.csv"

    def test_transform_get_file_standard(self, transformer):
        """
        Scenario: GET FILE='mydata.sav'. 
        Ensures standard SAV loading works even without the /FILE slash.
        """
        raw = "GET FILE='mydata.sav'."
        cmd = ParsedCommand(type=TokenType.FILE_READ, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 2
        assert isinstance(events[1], FileReadEvent)
        assert events[1].filename == "mydata.sav"

    def test_transform_match_files(self, transformer):
        raw = "MATCH FILES /FILE='A.sav' /TABLE='B.sav' /BY id."
        cmd = ParsedCommand(type=TokenType.FILE_MATCH, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 1
        assert isinstance(events[0], FileMatchEvent)
        assert "A.sav" in events[0].files
        assert "B.sav" in events[0].files

    def test_transform_assignment(self, transformer):
        raw = "COMPUTE bmi = weight / height."
        cmd = ParsedCommand(type=TokenType.ASSIGNMENT, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 1
        assert events[0].target.upper() == "BMI"
        assert any(d.upper() == "WEIGHT" for d in events[0].dependencies)

    def test_transform_recode(self, transformer):
        raw = "RECODE age (18 thru hi = 1) INTO is_adult."
        cmd = ParsedCommand(type=TokenType.RECODE, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 1
        assert isinstance(events[0], AssignmentEvent)
        assert events[0].target.upper() == "IS_ADULT"

    def test_transform_aggregate(self, transformer):
        raw = "AGGREGATE /OUTFILE=* /BREAK=region /sales_sum = SUM(sales)."
        cmd = ParsedCommand(type=TokenType.AGGREGATE, raw=raw)
        
        events = transformer.transform(cmd)
        
        assignment = next((e for e in events if isinstance(e, AssignmentEvent)), None)
        assert assignment is not None
        assert assignment.target == "sales_sum"
        assert "region" in assignment.dependencies

    def test_transform_aggregate_with_file_save(self, transformer):
        raw = "AGGREGATE /OUTFILE='summary.sav' /BREAK=x /y=MEAN(z)."
        cmd = ParsedCommand(type=TokenType.AGGREGATE, raw=raw)
        
        events = transformer.transform(cmd)
        
        save_event = next((e for e in events if isinstance(e, FileSaveEvent)), None)
        assert save_event is not None
        assert save_event.filename == "summary.sav"

    def test_ignores_self_dependency(self, transformer):
        raw = "COMPUTE x = x + 1."
        cmd = ParsedCommand(type=TokenType.ASSIGNMENT, raw=raw)
        
        events = transformer.transform(cmd)
        assert "X" not in [d.upper() for d in events[0].dependencies]