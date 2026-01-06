import pytest
from spss_engine.extractor import AssignmentExtractor


class TestAssignmentExtractor:

    def test_extract_compute_simple(self):
        """Test standard COMPUTE variable extraction."""
        cmd = "COMPUTE Age = 20."
        target = AssignmentExtractor.extract_target(cmd)
        assert target == "AGE"  # Expect normalization

    def test_extract_compute_with_whitespace(self):
        """Test extraction with messy whitespace."""
        cmd = "   COMPUTE   New_Var   =  x + y. "
        target = AssignmentExtractor.extract_target(cmd)
        assert target == "NEW_VAR"

    def test_extract_string_declaration(self):
        """Test extraction from variable declaration."""
        cmd = "STRING Employee_ID (A10)."
        target = AssignmentExtractor.extract_target(cmd)
        assert target == "EMPLOYEE_ID"

    def test_extract_recode_into(self):
        """Test RECODE with the INTO keyword."""
        cmd = "RECODE Age (0 thru 18=1) INTO Child_Group."
        target = AssignmentExtractor.extract_target(cmd)
        assert target == "CHILD_GROUP"

    def test_extract_recode_inplace(self):
        """Test RECODE in-place (modifies the original variable)."""
        cmd = "RECODE Age (0=1)."
        target = AssignmentExtractor.extract_target(cmd)
        assert target == "AGE"

    def test_unknown_command(self):
        """Test graceful failure for non-assignment commands."""
        cmd = "FREQUENCIES x."
        target = AssignmentExtractor.extract_target(cmd)
        assert target is None


    def test_extract_file_target(self):
        """
        Test extracting filenames from SAVE and MATCH commands.
        """
        extractor = AssignmentExtractor()
        
        # Case 1: SAVE OUTFILE (Single quotes)
        cmd1 = "SAVE OUTFILE='control_values.sav'."
        assert extractor.extract_file_target(cmd1) == "control_values.sav"
        
        # Case 2: SAVE TRANSLATE (Double quotes, mixed case)
        cmd2 = 'SAVE TRANSLATE /outfile="Monthly_Report.csv" /TYPE=CSV.'
        assert extractor.extract_file_target(cmd2) == "Monthly_Report.csv"
        
        # Case 3: MATCH FILES /TABLE (Lookup)
        cmd3 = "MATCH FILES /FILE=* /TABLE='benefit_rates.sav'."
        assert extractor.extract_file_target(cmd3) == "benefit_rates.sav"
        
        # Case 4: MATCH FILES /FILE (Merge)
        cmd4 = "MATCH FILES /FILE='part1.sav' /FILE='part2.sav'."
        # Our simple extractor should probably just grab the first valid file it finds 
        # or we might need to handle multiple. For now, let's target the first one.
        assert extractor.extract_file_target(cmd4) == "part1.sav"