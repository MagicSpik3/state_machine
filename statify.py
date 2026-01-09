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
from code_forge.R_runner import RRunner
from code_forge.generator import RGenerator
from spss_engine.pipeline import CompilerPipeline
from spss_engine.repository import Repository
from spss_engine.spss_runner import PsppRunner
from spec_writer.graph import GraphGenerator
from spec_writer.describer import SpecGenerator
from common.llm import OllamaClient
from spss_engine.inspector import SourceInspector  # 🟢 REQUIRED for robust file finding

# Setup Logging (Default INFO)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Statify")

def ensure_output_dir(base_output_dir: str, relative_path: str) -> str:
    """Creates the subdirectory structure in the output folder."""
    rel_dir = os.path.dirname(relative_path)
    target_dir = os.path.join(base_output_dir, rel_dir)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

# 🟢 NEW: Robust Dependency Copier
def copy_dependencies(code: str, source_dir: str, target_dir: str) -> List[str]:
    """
    Scans for data files using the SourceInspector and copies them.
    """
    inspector = SourceInspector()
    inputs, _ = inspector.scan(code)
    
    copied = []
    for filename in inputs:
        src_path = os.path.join(source_dir, filename)
        if os.path.exists(src_path):
            dst_path = os.path.join(target_dir, filename)
            try:
                shutil.copy(src_path, dst_path)
                copied.append(filename)
                logger.info(f"  📂 Copied dependency: {filename}")
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to copy {filename}: {e}")
    return copied

def process_file(full_path: str, relative_path: str, output_root: str, model: str, generate_code: bool, refine_mode: bool):
    """
    Orchestrates the conversion pipeline for a single file.
    """
    logger.info(f"📂 Processing {relative_path}...")
    
    # 0. Setup Output Location
    target_dir = ensure_output_dir(output_root, relative_path)
    base_name = os.path.splitext(os.path.basename(full_path))[0]
    
    with open(full_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Engine Phase (Parsing)
    logger.info("  ⚙️  Compiling Logic Graph...")
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # 2. Optimization Phase
    dead_vars = pipeline.analyze_dead_code()
    if dead_vars:
        logger.info(f"  🧹 Detected {len(dead_vars)} dead variable versions.")

    # 3. Verification Phase (Ground Truth Probe)
    runtime_values = {}
    if shutil.which("pspp"):
        logger.info("  🔬 Running Verification Probe (PSPP)...")
        try:
            runner = PsppRunner()
            runtime_values = runner.run_and_probe(full_path, output_dir=target_dir)
            logger.info(f"  ✅ Verification Successful. Captured {len(runtime_values)} values.")
        except Exception as e:
            logger.warning(f"  ⚠️ Verification Failed: {e}") 
            logger.debug(f"PSPP Error Details:", exc_info=True)
    else:
        logger.info("  ℹ️  PSPP not found. Skipping verification.")

    # 🟢 NEW: Copy Input Data (Before Code Gen)
    source_dir = os.path.dirname(full_path)
    input_files = copy_dependencies(code, source_dir, target_dir)

    # 4. Visualization Phase
    img_name = os.path.join(target_dir, f"{base_name}_flow")
    logger.info(f"  🎨 Rendering Graph to {img_name}.png...")
    
    try:
        # 🟢 FIX: Use .state directly
        graph_gen = GraphGenerator(pipeline.state)
        graph_gen.render(img_name)
    except Exception as e:
        logger.error(f"  ❌ Graph Generation Failed: {e}")

    # 5. Specification Phase
    logger.info(f"  🤖 Connecting to AI ({model})...")
    client = OllamaClient(model=model)
    
    # 🟢 FIX: Use .state directly
    generator = SpecGenerator(pipeline.state, client)
    
    logger.info("  📝 Writing Specification...")
    spec_content = generator.generate_report(dead_ids=dead_vars, runtime_values=runtime_values)
    
    report_file = os.path.join(target_dir, f"{base_name}_spec.md")
    with open(report_file, "w") as f:
        f.write(spec_content)

    # 6. Code Generation & Verification Phase
    if generate_code:
        logger.info("  ⚙️  Generating R Code...")
        
        # 🟢 FIX: Use .state directly
        r_gen = RGenerator(pipeline.state)
        
        # A. Rough Draft
        r_code = r_gen.generate_script()
        
        # B. AI Refinement
        if refine_mode:
            logger.info(f"  🧠 Refining code with qwen2.5-coder:latest...")
            try:
                refiner = CodeRefiner(model="qwen2.5-coder:latest")
                refined = refiner.refine(r_code)
                if refined:
                    r_code = refined
            except Exception as e:
                logger.warning(f"  ⚠️ Refinement failed, reverting to basic translation: {e}")

        # C. Save the Code
        r_path = os.path.join(target_dir, f"{base_name}.R")
        with open(r_path, "w", encoding="utf-8") as f:
            f.write(r_code)
            
        # D. Description File
        pkg_name = "".join(x for x in base_name if x.isalnum())
        desc_content = r_gen.generate_description(pkg_name)
        desc_path = os.path.join(target_dir, "DESCRIPTION")
        with open(desc_path, "w", encoding="utf-8") as f:
            f.write(desc_content)
        logger.info(f"  📦 Saved Package Metadata: {desc_path}")
        
        # 7. Equivalence Check (Run ONLY if we have ground truth)
        if runtime_values:
            logger.info("  ⚖️  Running Equivalence Check (Black Box vs White Box)...")
            
            # 🟢 FIX: Use .state directly
            r_runner = RRunner(r_path, state_machine=pipeline.state)
            
            # 🟢 FIX: Pass the discovered input file to force strict loading
            main_input = input_files[0] if input_files else None
            r_results = r_runner.run_and_capture(data_file=main_input)
            
            matches = 0
            mismatches = 0
            
            for key, legacy_raw in runtime_values.items():
                key = key.upper()
                if key in r_results:
                    new_val = r_results[key]
                    try:
                        leg_float = float(legacy_raw)
                        new_float = float(new_val)
                        if abs(leg_float - new_float) < 0.001:
                            matches += 1
                        else:
                            mismatches += 1
                            logger.error(f"    ❌ MISMATCH on {key}: SPSS={leg_float} | R={new_float}")
                    except (ValueError, TypeError):
                        leg_str = str(legacy_raw).strip().upper()
                        new_str = str(new_val).strip().upper()
                        if leg_str == new_str:
                            matches += 1
                        else:
                            mismatches += 1
                            logger.error(f"    ❌ MISMATCH on {key}: SPSS='{leg_str}' | R='{new_str}'")

            if matches > 0 and mismatches == 0:
                logger.info(f"  ✅ PROVEN EQUIVALENCE! ({matches} variables match perfectly)")
            elif mismatches > 0:
                logger.warning(f"  ⚠️  Equivalence Check Failed: {mismatches} mismatches found.")
            else:
                logger.warning("  ❓ No overlapping variables found to compare.")

        # 8. Architectural Review
        if refine_mode: 
            logger.info("  🏛️  Summoning the Architect...")
            
            architect = ProjectArchitect(OllamaClient(model="mistral:instruct"))
            logger.info("  🧐 The Architect is reviewing the project...")
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
            logger.error(f"❌ Failed to process {rel_path}: {e}", exc_info=True)
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
    
    # Verbose Flag
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    
    args = parser.parse_args()
    
    # Configure Logging Level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔧 Verbose mode enabled")
    
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