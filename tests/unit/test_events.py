import pytest
from spss_engine.events import (
    SemanticEvent, FileReadEvent, FileMatchEvent, 
    FileSaveEvent, AssignmentEvent, ScopeResetEvent
)

class TestSemanticEvents:
    """
    Verifies that the Event IR (Intermediate Representation) objects 
    correctly store and retrieve data.
    """

    def test_base_event_properties(self):
        """Ensure base class stores the raw command."""
        raw = "COMPUTE x = 1."
        event = SemanticEvent(source_command=raw)
        assert event.source_command == raw

    def test_file_read_event_defaults(self):
        """Verify defaults for FileReadEvent."""
        event = FileReadEvent(source_command="GET DATA...", filename="data.csv")
        
        assert event.filename == "data.csv"
        # 🟢 FIX: Expect 'TXT' as default (updated for intelligent loader)
        assert event.format == "TXT"  
        
        # 🟢 NEW: Check new metadata fields defaults
        assert event.delimiter == ","
        assert event.header_row is True
        assert event.variables == []

    def test_file_match_event_structure(self):
        """Verify FileMatchEvent handles multiple files."""
        files = ["A.sav", "B.sav"]
        event = FileMatchEvent(source_command="MATCH FILES...", files=files)
        assert len(event.files) == 2
        assert "A.sav" in event.files
        assert "B.sav" in event.files

    def test_assignment_event_structure(self):
        """Verify AssignmentEvent stores dependency graph info."""
        event = AssignmentEvent(
            source_command="COMPUTE x = y + z.",
            target="X",
            dependencies=["Y", "Z"],
            expression="y + z"
        )
        assert event.target == "X"
        assert "Y" in event.dependencies
        assert "Z" in event.dependencies

    def test_scope_reset_event(self):
        """Verify ScopeResetEvent stores the reason."""
        event = ScopeResetEvent(source_command="GET DATA...", reason="Destructive Load")
        assert event.reason == "Destructive Load"