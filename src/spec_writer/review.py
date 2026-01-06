import logging
import re
from typing import List, Dict
from common.llm import OllamaClient

logger = logging.getLogger("Architect")

ARCHITECT_PROMPT = (
    "You are a Senior Software Architect reviewing a legacy migration project.\n"
    "We have translated legacy SPSS code into R. Your job is to validate the coherence of the artifacts.\n\n"
    "--- ARTIFACT 1: THE SPECIFICATION ---\n"
    "{spec_summary}\n\n"
    "--- ARTIFACT 2: THE GENERATED R CODE ---\n"
    "{r_code}\n\n"
    "--- TASK ---\n"
    "1. **Library Check:** Does the R code import necessary libraries for the functions used (e.g. dplyr, lubridate)?\n"
    "2. **Logic Check:** Does the R code roughly match the intent described in the Specification?\n"
    "3. **Variable Check:** Are there 'ghost variables' used in R that weren't initialized?\n"
    "4. **Overall Grade:** Give a coherence score (1-10) and a brief summary of risks.\n\n"
    "Output your review in Markdown format."
)

class ProjectArchitect:
    def __init__(self, client: OllamaClient):
        self.llm = client

    def review(self, r_code: str, spec_content: str) -> str:
        """
        Conducts a holistic review of the project artifacts.
        """
        logger.info("  🧐 The Architect is reviewing the project...")
        
        # 1. Summarize Spec (it might be too long for context window)
        # We take the headers and the first few lines of each section
        spec_summary = self._summarize_spec(spec_content)
        
        # 2. Prepare Prompt
        prompt = ARCHITECT_PROMPT.format(
            spec_summary=spec_summary,
            r_code=r_code
        )
        
        # 3. Consult the AI
        try:
            review = self.llm.generate(prompt, max_tokens=1000)
            return review
        except Exception as e:
            logger.error(f"Architect failed to review: {e}")
            return "## Architect Review Failed\nCould not complete analysis."

    def _summarize_spec(self, full_spec: str) -> str:
        """Extracts headers and key descriptions to fit in context window."""
        lines = full_spec.split('\n')
        summary = []
        for line in lines:
            if line.startswith('#') or line.strip().startswith('* **'):
                summary.append(line)
        return "\n".join(summary[:50]) # Limit to first 50 key lines