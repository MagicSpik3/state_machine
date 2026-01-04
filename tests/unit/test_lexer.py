import pytest
from src.spss_engine.lexer import SpssLexer

class TestSpssLexer:

    def test_basic_command_splitting(self):
        """Test simple one-line commands."""
        raw_code = """
        COMPUTE x = 1.
        EXECUTE.
        """
        lexer = SpssLexer(raw_code)
        cmds = lexer.get_commands()
        
        assert len(cmds) == 2
        assert "COMPUTE x = 1." in cmds[0]
        assert "EXECUTE." in cmds[1]

    def test_multiline_command(self):
        """Test a command that spans multiple lines."""
        raw_code = """
        IF (x > 10)
           COMPUTE y = 20.
        """
        lexer = SpssLexer(raw_code)
        cmds = lexer.get_commands()
        
        assert len(cmds) == 1
        assert "IF (x > 10)" in cmds[0]
        assert "COMPUTE y = 20." in cmds[0]

    def test_decimal_handling(self):
        """Test that decimals don't trigger command termination."""
        raw_code = """
        COMPUTE ratio = 0.5.
        COMPUTE other = .05.
        """
        lexer = SpssLexer(raw_code)
        cmds = lexer.get_commands()
        
        assert len(cmds) == 2
        # Use normalize to check content easily
        assert lexer.normalize_command(cmds[0]) == "COMPUTE ratio = 0.5."
        assert lexer.normalize_command(cmds[1]) == "COMPUTE other = .05."

    def test_trailing_garbage(self):
        """Test handling of code that doesn't end cleanly."""
        raw_code = "COMPUTE x = 1" # No dot
        lexer = SpssLexer(raw_code)
        cmds = lexer.get_commands()
        
        assert len(cmds) == 1
        assert "COMPUTE x = 1" in cmds[0]

    def test_normalization(self):
        """Test stripping of excess whitespace."""
        raw_code = "   COMPUTE   x  =  1.   "
        lexer = SpssLexer(raw_code)
        cmd = lexer.get_commands()[0]
        normalized = lexer.normalize_command(cmd)
        
        assert normalized == "COMPUTE x = 1."