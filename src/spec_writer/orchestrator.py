import logging
from typing import List, Dict
from spss_engine.pipeline import CompilerPipeline
from spec_writer.conductor import Conductor
from spec_writer.describer import SpecGenerator
from common.llm import OllamaClient

logger = logging.getLogger("SpecOrchestrator")

class SpecOrchestrator:
    """
    Manages the generation of 'Mini-Specs' for each logic cluster
    and synthesizes them into a cohesive document.
    """
    def __init__(self, pipeline: CompilerPipeline, llm_client: OllamaClient):
        self.pipeline = pipeline
        self.conductor = Conductor(pipeline.state_machine)
        self.describer = SpecGenerator(pipeline.state_machine, llm_client)

    def generate_comprehensive_spec(self) -> str:
        # 1. Chunking: Identify Logical Clusters
        clusters = self.conductor.identify_clusters()
        logger.info(f"Orchestrator found {len(clusters)} logic clusters.")
        
        # 2. Mini-Specs: Generate Chapter for each Cluster
        chapters = []
        for i, cluster in enumerate(clusters):
            # Sort the cluster so the Describer reads it linearly
            sorted_node_ids = self.conductor._topological_sort(cluster)
            
            # Ask Describer to focus ONLY on these nodes
            chapter_content = self.describer.generate_chapter(
                chapter_index=i+1, 
                node_ids=sorted_node_ids
            )
            chapters.append(chapter_content)

        # 3. Oversight: Generate Executive Summary
        summary = self._generate_executive_summary(chapters)

        # 4. Assembly
        full_spec = f"# Comprehensive System Specification\n\n{summary}\n\n" + "\n\n".join(chapters)
        return full_spec

    def _generate_executive_summary(self, chapters: List[str]) -> str:
        """
        Scans the generated chapters to build a high-level map of the data flow.
        """
        summary_lines = ["## 🚀 Executive Summary", ""]
        summary_lines.append(f"The system is composed of **{len(chapters)} distinct processing stages**:")
        
        for i, chapter in enumerate(chapters):
            # Extract the title line from the chapter (heuristic)
            title = chapter.split('\n')[0].replace('#', '').strip()
            summary_lines.append(f"{i+1}. **{title}**")
            
        summary_lines.append("\n### 🔗 End-to-End Capabilities")
        summary_lines.append("This pipeline follows an **ETL -> Aggregation -> Calculation** pattern.")
        
        return "\n".join(summary_lines)