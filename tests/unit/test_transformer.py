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
        """
        Scenario: GET DATA /FILE='data.csv'
        Expectation: 1. ScopeResetEvent (Wipe memory), 2. FileReadEvent (Load data)
        """
        raw = "GET DATA /FILE='data.csv'."
        cmd = ParsedCommand(type=TokenType.FILE_READ, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 2
        assert isinstance(events[0], ScopeResetEvent)
        assert events[0].reason == "Destructive Load"
        
        assert isinstance(events[1], FileReadEvent)
        assert events[1].filename == "data.csv"

    def test_transform_file_read_unquoted(self, transformer):
        """Scenario: GET FILE = mydata. (Legacy unquoted syntax)"""
        raw = "GET FILE = mydata."
        cmd = ParsedCommand(type=TokenType.FILE_READ, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 2
        assert isinstance(events[1], FileReadEvent)
        assert events[1].filename == "mydata"

    def test_transform_match_files(self, transformer):
        """
        Scenario: MATCH FILES /FILE='A.sav' /TABLE='B.sav' /BY id.
        Expectation: Single FileMatchEvent with multiple files.
        """
        raw = "MATCH FILES /FILE='A.sav' /TABLE='B.sav' /BY id."
        cmd = ParsedCommand(type=TokenType.FILE_MATCH, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 1
        assert isinstance(events[0], FileMatchEvent)
        assert "A.sav" in events[0].files
        assert "B.sav" in events[0].files
        assert len(events[0].files) == 2

    def test_transform_assignment(self, transformer):
        """
        Scenario: COMPUTE bmi = weight / height.
        Expectation: AssignmentEvent with 'bmi' target and deps ['weight', 'height'].
        """
        raw = "COMPUTE bmi = weight / height."
        cmd = ParsedCommand(type=TokenType.ASSIGNMENT, raw=raw)
        
        # Note: This relies on the internal AssignmentExtractor working correctly
        events = transformer.transform(cmd)
        
        assert len(events) == 1
        event = events[0]
        assert isinstance(event, AssignmentEvent)
        assert event.target.upper() == "BMI"
        # We check specific dependencies usually found by the extractor
        # (Assuming your extractor logic handles basic arithmetic)
        assert any(d.upper() == "WEIGHT" for d in event.dependencies)

    def test_transform_recode(self, transformer):
        """
        Scenario: RECODE age (18 thru hi = 1) INTO is_adult.
        Expectation: AssignmentEvent treated similarly to COMPUTE.
        """
        raw = "RECODE age (18 thru hi = 1) INTO is_adult."
        cmd = ParsedCommand(type=TokenType.RECODE, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 1
        assert isinstance(events[0], AssignmentEvent)
        # Verify the transformer used the extractor to find the target 'is_adult'
        assert events[0].target.upper() == "IS_ADULT"

    def test_transform_aggregate(self, transformer):
        """
        Scenario: AGGREGATE /OUTFILE=* /BREAK=region /sales_sum = SUM(sales).
        Expectation: 
        1. AssignmentEvent for 'sales_sum' (depends on 'region')
        """
        raw = "AGGREGATE /OUTFILE=* /BREAK=region /sales_sum = SUM(sales)."
        cmd = ParsedCommand(type=TokenType.AGGREGATE, raw=raw)
        
        events = transformer.transform(cmd)
        
        # Expect at least one assignment event
        assignment = next((e for e in events if isinstance(e, AssignmentEvent)), None)
        assert assignment is not None
        assert assignment.target == "sales_sum"
        assert "region" in assignment.dependencies

    def test_transform_aggregate_with_file_save(self, transformer):
        """
        Scenario: AGGREGATE /OUTFILE='summary.sav' ...
        Expectation: Should emit a FileSaveEvent because OUTFILE != *
        """
        raw = "AGGREGATE /OUTFILE='summary.sav' /BREAK=x /y=MEAN(z)."
        cmd = ParsedCommand(type=TokenType.AGGREGATE, raw=raw)
        
        events = transformer.transform(cmd)
        
        save_event = next((e for e in events if isinstance(e, FileSaveEvent)), None)
        assert save_event is not None
        assert save_event.filename == "summary.sav"

    def test_ignores_self_dependency(self, transformer):
        """
        Scenario: COMPUTE x = x + 1.
        Expectation: 'x' should NOT be listed as a dependency of 'x'.
        """
        raw = "COMPUTE x = x + 1."
        cmd = ParsedCommand(type=TokenType.ASSIGNMENT, raw=raw)
        
        events = transformer.transform(cmd)
        
        assert len(events) == 1
        deps = [d.upper() for d in events[0].dependencies]
        assert "X" not in deps