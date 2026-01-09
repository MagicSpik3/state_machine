import pytest
from spss_engine.events import (
    SemanticEvent, FileReadEvent, FileMatchEvent, 
    FileSaveEvent, AssignmentEvent, ScopeResetEvent
)

class TestSemanticEvents:
    """
    Verifies the integrity of the Intermediate Representation (IR) Data Classes.
    """

    def test_base_event_properties(self):
        """Ensure all events carry the source command."""
        raw = "COMPUTE x=1."
        event = SemanticEvent(source_command=raw)
        assert event.source_command == raw

    def test_file_read_event_defaults(self):
        """Verify defaults for FileReadEvent."""
        event = FileReadEvent(source_command="GET DATA...", filename="data.csv")
        assert event.filename == "data.csv"
        assert event.format == "unknown"  # Default value check

    def test_file_match_event_structure(self):
        """Verify FileMatchEvent holds a list of files."""
        files = ["a.sav", "b.sav"]
        event = FileMatchEvent(source_command="MATCH FILES...", files=files)
        assert len(event.files) == 2
        assert "a.sav" in event.files
        assert event.is_join is True

    def test_assignment_event_structure(self):
        """Verify AssignmentEvent correctly stores dependency lists."""
        deps = ["age", "income"]
        event = AssignmentEvent(
            source_command="COMPUTE x = age + income.",
            target="x",
            dependencies=deps,
            expression="age + income"
        )
        assert event.target == "x"
        assert event.dependencies == deps
        assert event.expression == "age + income"

    def test_scope_reset_event(self):
        """Verify ScopeResetEvent carries a reason."""
        event = ScopeResetEvent(source_command="GET DATA...", reason="Destructive Load")
        assert event.reason == "Destructive Load"