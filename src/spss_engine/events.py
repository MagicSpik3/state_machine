from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class SemanticEvent:
    """Base class for all semantic events in the pipeline."""
    source_command: str

@dataclass
class FileReadEvent(SemanticEvent):
    """Represents a destructive load (GET DATA, GET FILE)."""
    filename: str
    format: str = "unknown"

@dataclass
class FileMatchEvent(SemanticEvent):
    """Represents a non-destructive merge (MATCH FILES)."""
    files: List[str]
    is_join: bool = True

@dataclass
class FileSaveEvent(SemanticEvent):
    """Represents an export (SAVE OUTFILE)."""
    filename: str

@dataclass
class AssignmentEvent(SemanticEvent):
    """Represents variable creation or mutation (COMPUTE, IF, RECODE)."""
    target: str
    dependencies: List[str]
    expression: str

@dataclass
class ScopeResetEvent(SemanticEvent):
    """Explicit instruction to wipe memory/start new cluster."""
    reason: str