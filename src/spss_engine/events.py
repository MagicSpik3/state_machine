from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class SemanticEvent:
    source_command: str

@dataclass
class FileReadEvent(SemanticEvent):
    """
    Represents a destructive load with specific parsing rules.
    """
    filename: str
    format: str = "TXT" # TXT, SAV, XLS
    delimiter: str = "," # Default csv
    qualifier: Optional[str] = '"'
    header_row: bool = True
    skip_rows: int = 0
    # List of (variable_name, spss_type_str) e.g., ('age', 'F8.0')
    variables: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class SemanticEvent:
    """Base class for all semantic events in the pipeline."""
    source_command: str


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