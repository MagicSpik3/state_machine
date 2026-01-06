# src/common/llm.py
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(
        self,
        model: str = "mistral:instruct",
        endpoint: str = "http://localhost:11434/api/generate",
        timeout: int = 120  # Increased default timeout
    ):
        self.model = model
        self.endpoint = endpoint
        self.timeout = timeout

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generates text from Ollama. Raises Exception on failure.
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": max_tokens},
        }
        
        try:
            response = requests.post(
                self.endpoint, 
                headers=headers, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            text = response.json().get("response", "").strip()
            
            # Clean generic markdown quotes
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            return text
            
        except requests.exceptions.ReadTimeout:
            logger.error(f"Ollama timed out after {self.timeout}s.")
            raise
        except Exception as e:
            logger.error(f"Ollama Error: {e}")
            raise