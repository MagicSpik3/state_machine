import logging
from typing import List, Dict
from spss_engine.state import StateMachine, VariableVersion
from spec_writer.conductor import Conductor
from common.llm import OllamaClient
from common.prompts import DESCRIBE_NODE_PROMPT, GENERATE_TITLE_PROMPT

logger = logging.getLogger(__name__)

class SpecGenerator:
    """
    Orchestrates the conversion of State Machine logic into a Structured Report.
    """
    def __init__(self, state_machine: StateMachine, llm_client: OllamaClient):
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
            chapter_title = self._generate_title(var_names)
            report_lines.append(f"## Chapter {i+1}: {chapter_title}")
            
            # 3. Describe Nodes
            for node_id in live_nodes:
                version_obj = self._find_version(node_id)
                if version_obj:
                    # Logic Description
                    desc = self._describe_node(node_id, version_obj.source, version_obj.dependencies)
                    line = f"* **{node_id}**: {desc}"
                    
                    # Add Runtime Verification (if available)
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

    def _describe_node(self, node_id: str, source: str, dependencies: List[str]) -> str:
        prompt = DESCRIBE_NODE_PROMPT.format(
            node_id=node_id, 
            dependencies=', '.join(dependencies), 
            source=source
        )
        try:
            return self.llm.generate(prompt)
        except Exception:
            return "Description unavailable (AI Error)"

    def _generate_title(self, variables: List[str]) -> str:
        sample = ", ".join(variables[:10])
        prompt = GENERATE_TITLE_PROMPT.format(variables=sample)
        try:
            return self.llm.generate(prompt, max_tokens=20)
        except Exception:
            return "Logic Cluster"