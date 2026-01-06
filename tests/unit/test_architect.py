import pytest
from unittest.mock import MagicMock
from spec_writer.review import ProjectArchitect

class TestProjectArchitect:
    
    def test_review_success(self):
        """
        Scenario: The Architect successfully reviews the artifacts.
        """
        # 1. Setup Mock LLM
        mock_client = MagicMock()
        mock_client.generate.return_value = "## Review\nGrade: 10/10\nLooks good!"
        
        # 2. Initialize Architect
        architect = ProjectArchitect(mock_client)
        
        # 3. Create Dummy Artifacts
        r_code = "library(dplyr)\ndf %>% mutate(x=1)"
        spec = "# Spec\n* **x**: Calculates value"
        
        # 4. Run Review
        result = architect.review(r_code, spec)
        
        # 5. Assertions
        assert "Grade: 10/10" in result
        
        # Verify the prompt contained the artifacts
        call_args = mock_client.generate.call_args[0][0]
        assert "library(dplyr)" in call_args
        assert "# Spec" in call_args

    def test_review_failure_handling(self):
        """
        Scenario: The AI crashes during review.
        """
        mock_client = MagicMock()
        mock_client.generate.side_effect = Exception("AI Timeout")
        
        architect = ProjectArchitect(mock_client)
        
        result = architect.review("code", "spec")
        
        # Should return a fallback message, not crash
        assert "Architect Review Failed" in result