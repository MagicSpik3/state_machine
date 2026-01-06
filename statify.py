import sys
import os
import argparse
import logging
import shutil
import os
import argparse
import logging
from typing import List


# --- LEGACY CORE (The Engine) ---
# These are the files still in src/spss_engine/
from spss_engine.pipeline import CompilerPipeline
from spss_engine.repository import Repository
from spss_engine.runner import PsppRunner

# --- SPEC WRITER (The Documenter) ---
# These are the files we just moved to src/spec_writer/
from spec_writer.conductor import Conductor
from spec_writer.graph import GraphGenerator
# FIX: Import 'SpecGenerator' instead of 'VariableDescriber'
from spec_writer.describer import SpecGenerator, OllamaClient, MockLLM


# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Statify")

def ensure_output_dir(base_output_dir: str, relative_path: str) -> str:
    """
    Creates the subdirectory structure in the output folder to match the source.
    Returns the full path to the specific output folder.
    """
    # Remove filename from relative path to get just the folder structure
    rel_dir = os.path.dirname(relative_path)
    target_dir = os.path.join(base_output_dir, rel_dir)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def process_file(full_path: str, relative_path: str, output_root: str, model: str):
    logger.info(f"📂 Processing {relative_path}...")
    
    # 0. Setup Output Location
    target_dir = ensure_output_dir(output_root, relative_path)
    base_name = os.path.splitext(os.path.basename(full_path))[0]
    
    with open(full_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Engine Phase
    logger.info("  ⚙️  Compiling Logic Graph...")
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # 2. Optimization Phase
    dead_vars = pipeline.analyze_dead_code()
    if dead_vars:
        logger.info(f"  🧹 Detected {len(dead_vars)} dead variable versions.")

    # 3. Verification Phase (Ground Truth)
    runtime_values = {}
    if shutil.which("pspp"):
        logger.info("  🔬 Running Verification Probe (PSPP)...")
        try:
            runner = PsppRunner()
            # We run the probe in the output dir to keep temp files out of source
            runtime_values = runner.run_and_probe(full_path, output_dir=target_dir)
            logger.info(f"  ✅ Verification Successful. Captured {len(runtime_values)} values.")
        except Exception as e:
            logger.warning(f"  ⚠️ Verification Failed: {e}")
    else:
        logger.info("  ℹ️  PSPP not found. Skipping verification.")

    # 4. Visualization Phase
    img_name = os.path.join(target_dir, f"{base_name}_flow")
    logger.info(f"  🎨 Rendering Graph to {img_name}.png...")
    GraphGenerator.render(
        pipeline.state_machine, 
        filename=img_name, 
        highlight_dead=dead_vars
    )

    # 5. Specification Phase
    logger.info(f"  🤖 Connecting to AI ({model})...")
    client = OllamaClient(model=model)
    generator = SpecGenerator(pipeline.state_machine, client)
    
    logger.info("  📝 Writing Specification...")
    report = generator.generate_report(dead_ids=dead_vars, runtime_values=runtime_values)
    
    # Save Report
    report_file = os.path.join(target_dir, f"{base_name}_spec.md")
    with open(report_file, "w") as f:
        f.write(report)
        
    logger.info(f"  ✨ Done: {report_file}")

def process_directory(source_root: str, output_root: str, model: str):
    logger.info(f"📂 Scanning Repository: {source_root}")
    logger.info(f"💾 Output Target: {output_root}")
    
    repo = Repository(source_root)
    repo.scan()
    
    files = repo.list_files()
    total = len(files)
    logger.info(f"🔎 Found {total} valid SPSS files.")
    
    errors = []
    
    for i, rel_path in enumerate(files, 1):
        full_path = repo.get_full_path(rel_path)
        print("-" * 60)
        logger.info(f"[{i}/{total}] Starting: {rel_path}")
        
        try:
            process_file(full_path, rel_path, output_root, model)
        except Exception as e:
            logger.error(f"❌ Failed to process {rel_path}: {e}")
            errors.append(rel_path)

    print("=" * 60)
    logger.info(f"🏁 Batch Complete. Success: {total - len(errors)}/{total}")
    if errors:
        logger.info(f"⚠️ Failed files: {errors}")

def main():
    parser = argparse.ArgumentParser(description="Statify: Convert Legacy Code to Human Specs")
    parser.add_argument("path", help="Path to SPSS source file or directory")
    parser.add_argument("--output", "-o", default="./dist", help="Directory to save generated documentation")
    parser.add_argument("--model", default="mistral:instruct", help="Ollama model to use")
    
    args = parser.parse_args()
    
    # Ensure absolute paths
    source_path = os.path.abspath(args.path)
    output_path = os.path.abspath(args.output)
    
    if os.path.isfile(source_path):
        # For single file, we treat the directory containing it as the root for relative pathing
        root_dir = os.path.dirname(source_path)
        rel_path = os.path.relpath(source_path, root_dir)
        process_file(source_path, rel_path, output_path, args.model)
    elif os.path.isdir(source_path):
        process_directory(source_path, output_path, args.model)
    else:
        logger.error(f"Path not found: {source_path}")

if __name__ == "__main__":
    main()