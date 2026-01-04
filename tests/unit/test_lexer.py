import pytest
from spss_engine.lexer import SpssLexer
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
        assert "0.5." in cmds[0]
        assert ".05." in cmds[1]

    def test_quoted_dot_handling(self):
        """
        CRITICAL: Test that a dot inside a string does NOT terminate the command.
        """
        raw_code = """
        COMPUTE msg = "End of sentence.".
        EXECUTE.
        """
        lexer = SpssLexer(raw_code)
        cmds = lexer.get_commands()
        
        # If logic is wrong, this will split into 2 or 3 commands incorrectly
        assert len(cmds) == 2
        assert 'msg = "End of sentence."' in cmds[0]

    def test_normalization(self):
        """Test stripping of excess whitespace."""
        raw_code = "   COMPUTE   x  =  1.   "
        lexer = SpssLexer(raw_code)
        cmd = lexer.get_commands()[0]
        normalized = lexer.normalize_command(cmd)
        
        assert normalized == "COMPUTE x = 1."