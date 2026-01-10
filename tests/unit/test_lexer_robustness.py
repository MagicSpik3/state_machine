import pytest
from spss_engine.lexer import SpssLexer

class TestLexerRobustness:
    """
    Verifies that the Lexer does not prematurely split commands
    containing internal dots (like F8.0 or filenames).
    """

    def test_lexer_handles_decimal_types(self):
        """
        Scenario: GET DATA with variable types containing dots (F8.0, F10.2).
        Concern: Lexer might split 'F10.0' into 'F10' and '0'.
        """
        code = """
        GET DATA /VARIABLES=
          id F8.0
          cost F10.2
          rate DOLLAR8.2.
        """
        
        lexer = SpssLexer()
        commands = lexer.split_commands(code)
        
        # Should be exactly 1 command.
        assert len(commands) == 1, f"Split incorrectly! Got: {commands}"
        
        cmd = commands[0]
        assert "F8.0" in cmd
        assert "F10.2" in cmd
        assert "DOLLAR8.2" in cmd

    def test_lexer_handles_dots_in_filenames(self):
        """
        Scenario: Filenames often have dots (data.v1.csv).
        """
        code = "GET DATA /FILE='my.data.v1.csv'."
        
        lexer = SpssLexer()
        commands = lexer.split_commands(code)
        
        assert len(commands) == 1
        assert "my.data.v1.csv" in commands[0]