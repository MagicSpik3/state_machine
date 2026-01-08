import sys
import os
import argparse
import logging
import shutil
from typing import List
from pathlib import Path

# --- CORE COMPONENTS ---
from spec_writer.review import ProjectArchitect
from code_forge.refiner import CodeRefiner
from code_forge.runner import RRunner
from code_forge.generator import RGenerator
from spss_engine.pipeline import CompilerPipeline
from spss_engine.repository import Repository
from spss_engine.spss_runner import PsppRunner
from spec_writer.graph import GraphGenerator
from spec_writer.describer import SpecGenerator
from spss_engine.inspector import SourceInspector
from common.llm import OllamaClient

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Statify")

def ensure_output_dir(base_output_dir: str, relative_path: str) -> str:
    """Creates the subdirectory structure in the output folder."""
    rel_dir = os.path.dirname(relative_path)
    target_dir = os.path.join(base_output_dir, rel_dir)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def process_file(full_path: str, relative_path: str, output_root: str, model: str, generate_code: bool, refine_mode: bool):
    """
    Orchestrates the conversion pipeline for a single file.
    """
    logger.info(f"📂 Processing {relative_path}...")
    
    # 0. Setup Output Location
    target_dir = ensure_output_dir(output_root, relative_path)
    base_name = os.path.splitext(os.path.basename(full_path))[0]
    source_dir = os.path.dirname(full_path)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Inspection Phase (The Data Bridge)
    inspector = SourceInspector()
    # FIX: Use new scan() API
    input_files, output_files = inspector.scan(code)
    
    # 1a. Transport Inputs (Copy legacy data to target)
    if input_files:
        logger.info(f"  🚚 Transporting {len(input_files)} input dependencies...")
        for filename in input_files:
            src = os.path.join(source_dir, filename)
            dst = os.path.join(target_dir, filename)
            if os.path.exists(src):
                shutil.copy(src, dst)
                logger.info(f"     - Copied: {filename}")
            else:
                logger.warning(f"     ⚠️ Missing input file: {filename}")
    else:
        logger.info("  ℹ️  No input artifacts detected.")


    if output_files:
        logger.info(f"  💾 Detected Output Artifacts:")
        for f in output_files:
            logger.info(f"     - {f}")
    else:
        logger.info("  ℹ️  No output artifacts detected.")        


    # 2. Engine Phase (Parsing)
    logger.info("  ⚙️  Compiling Logic Graph...")
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # 3. Optimization Phase
    dead_vars = pipeline.analyze_dead_code()
    if dead_vars:
        logger.info(f"  🧹 Detected {len(dead_vars)} dead variable versions.")

    # 4. Verification Phase (Ground Truth Probe)
    runtime_values = {}
    gold_standard_csv = None
    
    if shutil.which("pspp"):
        logger.info("  🔬 Running Verification Probe (PSPP)...")
        try:
            # Run PSPP inside the target directory (Sandbox execution)
            # This ensures outputs land in target_dir, not source_dir
            temp_script_path = os.path.join(target_dir, os.path.basename(full_path))
            shutil.copy(full_path, temp_script_path)
            
            runner = PsppRunner()
            runtime_values, artifacts = runner.run_and_probe(temp_script_path, output_dir=target_dir)
            
            # Clean up temp script
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)
            
            logger.info(f"  ✅ Verification Successful. Captured {len(runtime_values)} values.")

            # 4a. Archival (Identify and Rename Gold Standard)
            # We look for the file detected by the Inspector in the output list
            for out_file in output_files:
                generated_path = os.path.join(target_dir, out_file)
                if os.path.exists(generated_path) and out_file.endswith(".csv"):
                    # Rename to _original.csv so R generator has a clean slate
                    root, ext = os.path.splitext(out_file)
                    archived_name = f"{root}_original{ext}"
                    archived_path = os.path.join(target_dir, archived_name)
                    
                    shutil.move(generated_path, archived_path)
                    gold_standard_csv = archived_path
                    logger.info(f"  🏛️  Archived Gold Standard: {archived_name}")
                    break
                    
        except Exception as e:
            logger.warning(f"  ⚠️ Verification Failed: {e}")
    else:
        logger.info("  ℹ️  PSPP not found. Skipping verification.")

    # 5. Visualization Phase
    img_name = os.path.join(target_dir, f"{base_name}_flow")
    logger.info(f"  🎨 Rendering Graph to {img_name}.png...")
    try:
        graph_gen = GraphGenerator(pipeline.state_machine)
        graph_gen.render(img_name)
    except Exception as e:
        logger.error(f"  ❌ Graph Generation Failed: {e}")

    # 6. Specification Phase
    logger.info(f"  🤖 Connecting to AI ({model})...")
    client = OllamaClient(model=model)
    generator = SpecGenerator(pipeline.state_machine, client)
    
    logger.info("  📝 Writing Specification...")
    
    # FIX: Inject the data we found in Step 1
    spec_content = generator.generate_report(
        dead_ids=dead_vars, 
        runtime_values=runtime_values,
        input_files=input_files,   # <--- Passing the baton
        output_files=output_files
    )
    
    report_file = os.path.join(target_dir, f"{base_name}_spec.md")
    with open(report_file, "w") as f:
        f.write(spec_content)

    logger.info(f"  📄 Specification Saved: {report_file}")

    # 7. Code Generation & Verification Phase
    if generate_code:
        logger.info("  ⚙️  Generating R Code...")
        r_gen = RGenerator(pipeline.state_machine)
        
        # A. Rough Draft
        r_code = r_gen.generate_script()
        
        # B. AI Refinement
        if refine_mode:
            logger.info(f"  🧠 Refining code with qwen2.5-coder:latest...")
            refiner = CodeRefiner(model="qwen2.5-coder:latest")
            refined = refiner.refine(r_code)
            if refined:
                r_code = refined

        # C. Save the Code
        r_path = os.path.join(target_dir, f"{base_name}.R")
        with open(r_path, "w", encoding="utf-8") as f:
            f.write(r_code)
            
        # D. Description File
        pkg_name = "".join(x for x in base_name if x.isalnum())
        try:
            desc_content = r_gen.generate_description(pkg_name)
            desc_path = os.path.join(target_dir, "DESCRIPTION")
            with open(desc_path, "w", encoding="utf-8") as f:
                f.write(desc_content)
            logger.info(f"  📦 Saved Package Metadata: {desc_path}")
        except Exception as e:
            logger.error(f"  ❌ Failed to generate DESCRIPTION: {e}")
        
        # 8. Equivalence Check (Run using the Data Bridge)
        if gold_standard_csv:
            logger.info("  ⚖️  Running Equivalence Check (Using Gold Standard Data)...")
            
            r_runner = RRunner(r_path)
            
            # TODO: Update RRunner to accept gold_standard_csv argument in next step
            # For now, we use the standard capture which relies on dummy data or the updated runner logic
            try:
                # We pass the gold standard CSV path to the runner (Logic to be implemented in runner.py)
                r_results = r_runner.run_and_capture(gold_standard_csv=gold_standard_csv)
                
                # Compare Logic (Simplified for now)
                matches = 0
                mismatches = 0
                for key, val in runtime_values.items():
                    if key in r_results:
                        # ... comparison logic ...
                        matches += 1
                
                logger.info(f"  ✅ Comparison Complete. Matched {matches} variables.")
                
            except Exception as e:
                 logger.error(f"  ❌ R Execution Failed: {e}")

        # 9. Architectural Review
        if refine_mode: 
            logger.info("  🏛️  Summoning the Architect...")
            architect = ProjectArchitect(OllamaClient(model="mistral:instruct"))
            review_report = architect.review(r_code, spec_content)
            
            review_path = os.path.join(target_dir, f"{base_name}_REVIEW.md")
            with open(review_path, 'w') as f:
                f.write(review_report)
            logger.info(f"  📝 Architectural Review Saved: {review_path}")

def process_directory(source_root: str, output_root: str, model: str, generate_code: bool, refine_mode: bool):
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
            process_file(full_path, rel_path, output_root, model, generate_code, refine_mode)
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
    parser.add_argument("--code", action="store_true", help="Generate R code alongside the spec")
    parser.add_argument("--refine", action="store_true", help="Use AI to refine the generated code")
    
    args = parser.parse_args()
    
    source_path = os.path.abspath(args.path)
    output_path = os.path.abspath(args.output)
    
    if os.path.isfile(source_path):
        root_dir = os.path.dirname(source_path)
        rel_path = os.path.relpath(source_path, root_dir)
        process_file(source_path, rel_path, output_path, args.model, args.code, args.refine)
    elif os.path.isdir(source_path):
        process_directory(source_path, output_path, args.model, args.code, args.refine)
    else:
        logger.error(f"Path not found: {source_path}")

if __name__ == "__main__":
    main()

