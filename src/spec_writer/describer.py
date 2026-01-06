import requests
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict
from spss_engine.state import StateMachine, VariableVersion
from spec_writer.conductor import Conductor

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    @abstractmethod
    def describe_node(self, node_id: str, source: str, dependencies: List[str]) -> str:
        pass

    @abstractmethod
    def generate_title(self, variables: List[str]) -> str:
        """Generates a short title for a cluster of variables."""
        pass

class MockLLM(LLMClient):
    def describe_node(self, node_id: str, source: str, dependencies: List[str]) -> str:
        # FIX: We must include dependencies in the string so the test can assert they were passed correctly.
        dep_str = ", ".join(dependencies)
        return f"Description of {node_id} (Source: {source}) (Deps: {dep_str})"
        
    def generate_title(self, variables: List[str]) -> str:
        return "Logic Cluster"


class OllamaClient(LLMClient):
    def __init__(
        self,
        model: str = "mistral:instruct",
        endpoint: str = "http://localhost:11434/api/generate",
    ):
        self.model = model
        self.endpoint = endpoint

    def _call_ollama(self, prompt: str, max_tokens: int = 150) -> str:
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": max_tokens},
        }
        try:
            response = requests.post(
                self.endpoint, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()
            text = response.json().get("response", "").strip()
            # Clean quotes
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            return text
        except Exception as e:
            logger.error(f"Ollama Error: {e}")
            return "[AI Error]"

    def describe_node(self, node_id: str, source: str, dependencies: List[str]) -> str:
        prompt = (
            f"You are a Business Analyst. Describe this logic step in ONE sentence.\n"
            f"Context: {node_id} depends on {', '.join(dependencies)}\n"
            f"Code: {source}\n"
            f"Description:"
        )
        return self._call_ollama(prompt)

    def generate_title(self, variables: List[str]) -> str:
        # If the cluster is huge, just take the first 10 vars to avoid context limits
        sample = ", ".join(variables[:10])
        prompt = (
            f"Summarize these variables into a 3-5 word Title.\n"
            f"Variables: {sample}\n"
            f"Title:"
        )
        return self._call_ollama(prompt, max_tokens=20)
    
    
class SpecGenerator:
    """
    Orchestrates the conversion of State Machine logic into a Structured Report.
    """
    def __init__(self, state_machine: StateMachine, llm_client: LLMClient):
        self.state_machine = state_machine
        self.llm = llm_client
        self.conductor = Conductor(state_machine)

    def generate_report(self, dead_ids: List[str] = None, runtime_values: Dict[str, str] = None) -> str:
        if dead_ids is None: dead_ids = []
        if runtime_values is None: runtime_values = {}
            
        # 1. Get Organized Chapters (Clusters)
        clusters = self.conductor.identify_clusters()
        
        report_lines = ["# Business Logic Specification", ""]
        
        # Add Verification Badge
        if runtime_values:
            report_lines.append("### ✅ Verified Execution")
            report_lines.append(f"This logic was cross-referenced against a live PSPP execution.")
            report_lines.append("")
        
        for i, cluster_nodes in enumerate(clusters):
            # Filter dead nodes from this cluster
            live_nodes = [nid for nid in cluster_nodes if nid not in dead_ids]
            
            if not live_nodes:
                continue
                
            # 2. Extract Variable Names for Titling
            var_names = list(set([nid.rsplit('_', 1)[0] for nid in live_nodes]))
            chapter_title = self.llm.generate_title(var_names)
            report_lines.append(f"## Chapter {i+1}: {chapter_title}")
            
            # 3. Describe Nodes
            for node_id in live_nodes:
                version_obj = self._find_version(node_id)
                if version_obj:
                    # Logic Description
                    desc = self.llm.describe_node(node_id, version_obj.source, version_obj.dependencies)
                    line = f"* **{node_id}**: {desc}"
                    
                    # Add Runtime Verification (if available)
                    # Node ID is "NET_PAY_0", but PSPP CSV usually returns "NET_PAY".
                    # We map by variable name.
                    var_name = node_id.rsplit('_', 1)[0]
                    if var_name in runtime_values:
                        val = runtime_values[var_name]
                        line += f" <br> *Example Value: `{val}`*"
                    
                    report_lines.append(line)
            
            report_lines.append("")
            
        return "\n".join(report_lines)

    def _find_version(self, node_id: str) -> VariableVersion:
        var_name = node_id.rsplit('_', 1)[0]
        history = self.state_machine.get_history(var_name)
        for v in history:
            if v.id == node_id:
                return v
        return None