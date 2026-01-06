import pytest
from code_forge.rosetta import RosettaStone

class TestRosettaStone:
    
    def test_constants(self):
        """Test simple constant replacement."""
        assert RosettaStone.translate_expression("$SYSMIS") == "NA"

    def test_simple_functions(self):
        """Test direct function mapping."""
        assert RosettaStone.translate_expression("TRUNC(x)") == "trunc(x)"
        assert RosettaStone.translate_expression("MAX(a, b)") == "pmax(a, b)"

    def test_mod_operator(self):
        """Test converting MOD(a, b) -> (a %% b)."""
        # Basic
        assert RosettaStone.translate_expression("MOD(a, b)") == "(a %% b)"
        # Case Insensitive
        assert RosettaStone.translate_expression("Mod(X, 100)") == "(X %% 100)"

    def test_date_mdy_simple(self):
        """Test argument swapping: MDY -> YMD."""
        # SPSS: DATE.MDY(Month, Day, Year) -> R: make_date(Year, Month, Day)
        assert RosettaStone.translate_expression("DATE.MDY(12, 31, 2022)") == "make_date(2022, 12, 31)"

    def test_date_mdy_complex_nesting(self):
        """
        The Boss Level: DATE.MDY with nested commas and function calls.
        SPSS: DATE.MDY( TRUNC(MOD(x,10000)/100), MOD(x,100), TRUNC(x/10000) )
        """
        spss = "DATE.MDY(TRUNC(MOD(dob_num,10000)/100), MOD(dob_num,100), TRUNC(dob_num/10000))"
        
        r_code = RosettaStone.translate_expression(spss)
        
        # 1. Structure Check
        assert r_code.startswith("make_date(")
        
        # 2. Argument Swap Check
        # The Year (TRUNC(dob_num/10000)) should now be first
        assert "make_date(trunc(dob_num/10000)" in r_code
        
        # 3. Recursive Translation Check
        # The inner MOD should be converted to %%
        assert "%%" in r_code
        assert "MOD" not in r_code

    def test_split_args_logic(self):
        """Unit test for the helper that splits arguments while respecting parens."""
        expression = "trunc(a, b), c, d(e, f)"
        expected = ["trunc(a, b)", "c", "d(e, f)"]
        assert RosettaStone._split_args(expression) == expected

    def test_number_conversion(self):
        """Test parsing NUMBER(var, format)."""
        assert RosettaStone.translate_expression("NUMBER(str_var, F8.0)") == "as.numeric(str_var)"