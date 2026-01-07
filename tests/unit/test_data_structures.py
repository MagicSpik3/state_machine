import pytest
from spss_engine.state import VariableVersion, ClusterMetadata
from spss_engine.parser import TokenType, ParsedCommand

class TestDataStructures:
    """
    Verifies the fundamental data carriers of the SPSS Engine.
    """

    def test_variable_version_integrity(self):
        # Verify ID generation and default values
        v = VariableVersion(name="AGE", version=1, source="COMPUTE...", cluster_index=5)
        assert v.id == "AGE_1"
        assert v.dependencies == [] # Default factory check

    def test_cluster_metadata_defaults(self):
        # Verify set initialization
        c = ClusterMetadata(index=0)
        assert isinstance(c.inputs, set)
        assert isinstance(c.outputs, set)
        assert c.node_count == 0

    def test_parsed_command_structure(self):
        # Verify Enum and Dataclass interaction
        cmd = ParsedCommand(TokenType.ASSIGNMENT, "COMPUTE x=1.")
        assert cmd.type == TokenType.ASSIGNMENT
        assert cmd.raw == "COMPUTE x=1."