import pytest
from unittest.mock import MagicMock, patch
from common.llm import OllamaClient
from common.prompts import DESCRIBE_NODE_PROMPT
import requests

class TestOllamaClient:
    
    @patch('common.llm.requests.post')
    def test_generate_success(self, mock_post):
        """Test successful generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Refined Code"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("Test Prompt")
        
        assert result == "Refined Code"
        mock_post.assert_called_once()

    @patch('common.llm.requests.post')
    def test_timeout_handling(self, mock_post):
        """Test that timeouts are raised properly."""
        mock_post.side_effect = requests.exceptions.ReadTimeout("Timeout!")
        
        client = OllamaClient(timeout=1)
        
        with pytest.raises(requests.exceptions.ReadTimeout):
            client.generate("Test")

    def test_prompt_formatting(self):
        """Test that prompts format correctly."""
        formatted = DESCRIBE_NODE_PROMPT.format(
            node_id="VAR_A", 
            dependencies="VAR_B", 
            source="COMPUTE X=1"
        )
        assert "VAR_A" in formatted
        assert "COMPUTE X=1" in formatted