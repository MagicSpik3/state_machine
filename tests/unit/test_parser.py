import pytest
from spss_engine.parser import SpssParser, TokenType

class TestSpssParser:

    @pytest.fixture
    def parser(self):
        """Fixture to provide a fresh parser instance for each test."""
        return SpssParser()

    # --- Regression Tests (The "Old" Tests) ---
    
    def test_identify_assignment(self, parser):
        """Test COMPUTE is detected as ASSIGNMENT."""
        cmd = "COMPUTE Age = 25."
        result = parser.parse_command(cmd)
        assert result.type == TokenType.ASSIGNMENT
        assert result.raw == cmd

    def test_identify_conditional(self, parser):
        """Test IF and DO IF are detected as CONDITIONAL."""
        assert parser.parse_command("IF (x > 10)").type == TokenType.CONDITIONAL
        assert parser.parse_command("DO IF (Status = 1)").type == TokenType.CONDITIONAL

    def test_identify_recode_as_assignment(self, parser):
        """Test RECODE and STRING are detected as ASSIGNMENT."""
        assert parser.parse_command("RECODE x (1=2).").type == TokenType.ASSIGNMENT
        assert parser.parse_command("STRING Name (A20).").type == TokenType.ASSIGNMENT

    def test_identify_passthrough(self, parser):
        """Test unknown commands (like FREQUENCIES) are PASSTHROUGH."""
        cmd = "FREQUENCIES VARIABLES=Age."
        result = parser.parse_command(cmd)
        assert result.type == TokenType.PASSTHROUGH

    # --- New Feature Tests (File I/O) ---

    def test_identify_file_save(self, parser):
        """Test detection of SAVE commands."""
        # Standard .sav save
        assert parser.parse_command("SAVE OUTFILE='data.sav'.").type == TokenType.FILE_SAVE
        # Export to CSV
        assert parser.parse_command("SAVE TRANSLATE /OUTFILE='data.csv'.").type == TokenType.FILE_SAVE

    def test_identify_file_match(self, parser):
        """Test detection of MATCH FILES commands."""
        cmd = "MATCH FILES /FILE=* /TABLE='lookup.sav'."
        assert parser.parse_command(cmd).type == TokenType.FILE_MATCH


        