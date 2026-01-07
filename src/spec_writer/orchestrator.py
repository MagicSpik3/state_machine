from typing import Dict, List, Optional
import logging
import os
from common.llm import OllamaClient
from spss_engine.pipeline import CompilerPipeline
from spec_writer.describer import SpecGenerator
from spec_writer.graph import GraphGenerator
from spec_writer.review import ProjectArchitect

logger = logging.getLogger("Orchestrator")

class SpecOrchestrator:
    def __init__(self, llm_client: Optional[OllamaClient] = None):
        self.pipeline = CompilerPipeline()
        self.llm_client = llm_client if llm_client else OllamaClient()
        self.generator = None 

    def ingest(self, file_path: str):
        logger.info(f"Processing {os.path.basename(file_path)}...")
        self.pipeline.process_file(file_path)
        self.generator = SpecGenerator(self.pipeline.state_machine, self.llm_client)

    def generate_comprehensive_spec(self, output_dir: str, filename_root: str):
        if not self.generator:
            raise ValueError("No file ingested. Call ingest() first.")

        # 1. Analyze Dead Code
        dead_ids = self.pipeline.analyze_dead_code()
        
        # 2. Render Graph (FIXED INSTANCE CALL)
        # Instantiate the generator with state
        graph_gen = GraphGenerator(self.pipeline.state_machine)
        
        # Define base path (Graphviz appends extension)
        graph_base_path = os.path.join(output_dir, f"{filename_root}_flow")
        
        logger.info(f"Rendering Graph to {graph_base_path}...")
        
        # CORRECT CALL: Just pass the positional path argument.
        # DO NOT use 'filename=' or 'format='.
        graph_gen.render(graph_base_path)

        # 3. Generate Spec
        spec_md = self.generator.generate_report(
            dead_ids=dead_ids, 
            runtime_values={} 
        )

        # 4. Save Artifact
        os.makedirs(output_dir, exist_ok=True)
        md_path = os.path.join(output_dir, f"{filename_root}_spec.md")
        with open(md_path, "w") as f:
            f.write(spec_md)
        
        logger.info(f"Spec generated at: {md_path}")
        return md_path