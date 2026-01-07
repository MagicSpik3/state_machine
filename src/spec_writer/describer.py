from typing import Dict, List, Optional
import logging
from common.llm import OllamaClient
from spss_engine.state import StateMachine, VariableVersion
from spec_writer.conductor import Conductor

GENERATE_TITLE_PROMPT = "Generate a short, business-friendly title for this logic cluster. Context: {context}"
DESCRIBE_NODE_PROMPT = "Explain the business logic of this SPSS command in plain English. Code: {code}"

logger = logging.getLogger("SpecGenerator")

class SpecGenerator:
    def __init__(self, state_machine: StateMachine, llm_client: OllamaClient):
        self.state_machine = state_machine
        self.llm_client = llm_client
        self.conductor = Conductor(state_machine)

    def generate_report(self, dead_ids: List[str] = None, runtime_values: Dict[str, str] = None) -> str:
        if dead_ids is None: dead_ids = []
        if runtime_values is None: runtime_values = {}

        clusters = self.conductor.identify_clusters()
        report_parts = ["# Business Logic Specification", ""]

        for i, cluster_node_ids in enumerate(clusters):
            if not cluster_node_ids:
                continue

            chapter_num = i + 1
            
            # 1. Generate Chapter Title
            context_nodes = cluster_node_ids[:5] 
            context_str = " ".join([self._get_node_source(nid) for nid in context_nodes])
            
            title_prompt = GENERATE_TITLE_PROMPT.format(context=context_str)
            try:
                chapter_title = self.llm_client.generate(title_prompt).strip()
            except Exception:
                chapter_title = "Logic Cluster"

            if not chapter_title or "Generated" in chapter_title: 
                 chapter_title = "Logic Cluster"

            report_parts.append(f"## Chapter {chapter_num}: {chapter_title}")
            
            # 2. Describe Nodes
            sorted_ids = self.conductor._topological_sort(cluster_node_ids)
            
            for node_id in sorted_ids:
                if node_id in dead_ids: continue
                
                node = self._find_node_by_id(node_id)
                if not node: continue

                try:
                    description = self._describe_node(node)
                except Exception:
                    description = "Logic description unavailable."

                report_parts.append(f"* **{node.id}**: {description}")
                # FIX: Add Source Code to output to pass verification tests
                report_parts.append(f"  > `{node.source.strip()}`")

            report_parts.append("")

        return "\n".join(report_parts)

    def _find_node_by_id(self, node_id: str) -> Optional[VariableVersion]:
        for node in self.state_machine.nodes:
            if node.id == node_id:
                return node
        return None

    def _get_node_source(self, node_id: str) -> str:
        node = self._find_node_by_id(node_id)
        return node.source if node else ""

    def _describe_node(self, node: VariableVersion) -> str:
        prompt = DESCRIBE_NODE_PROMPT.format(code=node.source)
        return self.llm_client.generate(prompt).strip()