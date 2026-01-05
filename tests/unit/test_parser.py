import pytest
from spss_engine.parser import SpssParser, TokenType


class TestSpssParser:

    def test_identify_assignment(self):
        """Test detection of simple COMPUTE statements."""
        cmd = "COMPUTE x = 1."
        parsed = SpssParser.parse_command(cmd)

        assert parsed.type == TokenType.ASSIGNMENT
        assert parsed.raw == cmd
        # Ideally, we eventually want to extract 'x' and '1',
        # but for step 1, just identifying the TYPE is enough.

    def test_identify_conditional(self):
        """Test detection of IF statements."""
        cmd = "IF (Age > 18)"  # Note: Lexer might strip the dot or keep it.
        parsed = SpssParser.parse_command(cmd)

        assert parsed.type == TokenType.CONDITIONAL

    def test_identify_passthrough(self):
        """Test that unknown/analysis commands are marked as passthrough."""
        cmd = "FREQUENCIES VARIABLES=Age."
        parsed = SpssParser.parse_command(cmd)

        assert parsed.type == TokenType.PASSTHROUGH

    def test_identify_recode_as_assignment(self):
        """RECODE changes state, so it must be an assignment."""
        cmd = "RECODE Age (0 thru 18=1) INTO Child_Flag."
        parsed = SpssParser.parse_command(cmd)

        assert parsed.type == TokenType.ASSIGNMENT
