import pytest
from spss_engine.parser import SpssParser, TokenType

class TestSpssParser:
    def setup_method(self):
        self.parser = SpssParser()

    def test_identify_assignment(self):
        cmd = "COMPUTE x = 1."
        parsed = self.parser.parse_command(cmd)
        assert parsed.type == TokenType.ASSIGNMENT
        assert parsed.raw == cmd # Now works because of the property alias

    def test_identify_conditional(self):
        cmd = "IF (x > 1) y = 2."
        parsed = self.parser.parse_command(cmd)
        assert parsed.type == TokenType.CONDITIONAL


    def test_identify_recode_as_assignment(self):
        # 🟢 UPDATED: Expect TokenType.RECODE, not ASSIGNMENT
        cmd = "RECODE x (1=2)."
        parsed = self.parser.parse_command(cmd)
        assert parsed.type == TokenType.RECODE


    def test_identify_file_save(self):
        cmd = "SAVE OUTFILE='data.sav'."
        parsed = self.parser.parse_command(cmd)
        assert parsed.type == TokenType.FILE_SAVE

    def test_identify_match_files(self):
        cmd = "MATCH FILES /TABLE='x.sav'."
        parsed = self.parser.parse_command(cmd)
        assert parsed.type == TokenType.FILE_MATCH