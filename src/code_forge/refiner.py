import logging
from common.llm import OllamaClient

logger = logging.getLogger("CodeRefiner")

import logging
from common.llm import OllamaClient
from common.prompts import REFINE_CODE_PROMPT

logger = logging.getLogger("CodeRefiner")

class CodeRefiner:
    def __init__(self, model="qwen2.5-coder:latest"):
        # Set a generous timeout for code generation
        self.client = OllamaClient(model=model, timeout=180)

    def refine(self, rough_code: str) -> str:
        logger.info(f"  🧠 Refining code with {self.client.model}...")
        
        prompt = REFINE_CODE_PROMPT.format(code=rough_code)
        
        try:
            refined_code = self.client.generate(prompt, max_tokens=2000)
            
            # Clean markdown code blocks
            refined_code = refined_code.replace("```r", "").replace("```", "").strip()
            
            return refined_code
            
        except Exception as e:
            logger.warning(f"  ⚠️ AI Refinement failed (using Rough Draft): {e}")
            return rough_code  # <--- SAFETY FALLBACK
