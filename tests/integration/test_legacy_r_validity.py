import pytest
import os
from code_forge.R_runner import RRunner

class TestLegacyRValidity:
    
    def test_repro_legacy_syntax_error(self, tmp_path):
        """
        Tests the actual generated code from the real project to confirm it fails
        and identify why (DATE.MDY and 'value').
        """
        # The exact code output you provided
        bad_code = """
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)
        
        logic_pipeline <- function(df) {
          df <- df %>%
            mutate(min_age_n = as.numeric(value)) %>%  # FAIL 1: 'value' not found
            mutate(dob_date = DATE.MDY(                # FAIL 2: DATE.MDY not in R
              trunc((dob_num %%10000)/100),
              (dob_num %%100),
              trunc(dob_num/10000)
            ))
          return(df)
        }
        """
        
        script = tmp_path / "bad_legacy.R"
        script.write_text(bad_code, encoding="utf-8")
        
        runner = RRunner(str(script))
        # Initialize inputs so we don't fail on missing columns
        result = runner.run_and_capture(input_vars=['dob_num', 'value'])
        
        # Should fail
        assert result == {}, "The legacy code should fail due to syntax/runtime errors"

    def test_fix_legacy_logic(self, tmp_path):
        """
        Verifies that fixing DATE.MDY -> make_date(y,m,d) and 
        resolving 'value' makes the code runnable.
        """
        # The Fixed Code:
        # 1. 'value' -> changed to 'min_age' (assuming that's the source)
        # 2. DATE.MDY(m,d,y) -> make_date(y,m,d)
        fixed_code = """
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)
        
        logic_pipeline <- function(df) {
          df <- df %>%
            mutate(min_age_n = as.numeric(min_age)) %>% 
            mutate(dob_date = make_date(
              trunc(dob_num/10000),           # Year
              trunc((dob_num %%10000)/100),   # Month
              (dob_num %%100)                 # Day
            ))
          return(df)
        }
        """
        
        script = tmp_path / "fixed_legacy.R"
        script.write_text(fixed_code, encoding="utf-8")
        
        runner = RRunner(str(script))
        
        # Run with dummy data: 1990-01-01 (19900101)
        # min_age = "10"
        result = runner.run_and_capture(input_vars=['dob_num', 'min_age'])
        
        assert result != {}, "The fixed code should run successfully"