import pytest
import os
from code_forge.runner import RRunner

class TestRSyntaxRepro:
    
    def test_repro_syntax_error(self, tmp_path):
        """
        Reproduces the 'unexpected end of input' or parsing error 
        found in the generated payroll.R file.
        """
        # 1. The Broken Code (From your cat output)
        # We assume the error is likely the weird '.[x]' or 'value' usage
        bad_r_code = """
        library(dplyr)
        library(readr)
        library(lubridate)
        
        logic_pipeline <- function(df) {
            df <- df %>%
                mutate(across(starts_with('min_age_n'), ~as.numeric(value), .names = 'min_age_n')) %>%
                mutate(across(starts_with('dob_date'), ~make_date(trunc((.x %%10000)/100), (.[x] %%100), trunc(.x/10000)), .names = 'dob_date'))
            return(df)
        }
        """
        
        script_path = tmp_path / "bad_script.R"
        script_path.write_text(bad_r_code, encoding="utf-8")
        
        runner = RRunner(str(script_path))
        
        # We expect this to fail (return empty dict) and log an error
        # Note: We pass 'min_age_n' to initialize it so it doesn't fail on "object not found"
        result = runner.run_and_capture(input_vars=['min_age_n', 'dob_date'])
        
        # If result is empty, it failed as expected
        assert result == {}, "Bad code should fail"

    def test_fix_syntax_error(self, tmp_path):
        """
        Verifies that fixing the syntax (.x instead of .[x] and value) works.
        """
        # 2. The Fixed Code
        # - Replaced 'value' with '.x'
        # - Replaced '.[x]' with '.x'
        fixed_r_code = """
        library(dplyr)
        library(readr)
        library(lubridate)
        
        logic_pipeline <- function(df) {
            df <- df %>%
                mutate(across(starts_with('min_age_n'), ~as.numeric(.x), .names = 'min_age_n')) %>%
                mutate(across(starts_with('dob_date'), ~make_date(trunc((.x %%10000)/100), (.x %%100), trunc(.x/10000)), .names = 'dob_date'))
            return(df)
        }
        """
        
        script_path = tmp_path / "good_script.R"
        script_path.write_text(fixed_r_code, encoding="utf-8")
        
        runner = RRunner(str(script_path))
        
        # We initialize with some dummy data to ensure it runs
        # 'min_age_n' = 0, 'dob_date' = 0 (numeric)
        result = runner.run_and_capture(input_vars=['min_age_n', 'dob_date'])
        
        # If result is NOT empty, it succeeded
        # (It will return the last row of the result df)
        assert result != {}, "Fixed code should run successfully"