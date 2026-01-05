import sys
import os
import argparse
import logging
from spss_engine.pipeline import CompilerPipeline
from spss_engine.describer import SpecGenerator, OllamaClient
from spss_engine.graph import GraphGenerator

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("Statify")

def process_file(file_path: str, model: str):
    logger.info(f"📂 Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Engine Phase
    logger.info("⚙️  Compiling Logic Graph...")
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # 2. Optimization Phase
    dead_vars = pipeline.analyze_dead_code()
    if dead_vars:
        logger.info(f"🧹 Detected {len(dead_vars)} dead variable versions.")

    # 3. Visualization Phase
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    img_name = f"{base_name}_flow"
    logger.info(f"🎨 Rendering Graph to {img_name}.png...")
    GraphGenerator.render(
        pipeline.state_machine, 
        filename=img_name, 
        highlight_dead=dead_vars
    )

    # 4. Specification Phase
    logger.info(f"🤖 Connecting to AI ({model}) for Chapter Generation...")
    client = OllamaClient(model=model)
    generator = SpecGenerator(pipeline.state_machine, client)
    
    logger.info("📝 Writing Specification...")
    report = generator.generate_report(dead_ids=dead_vars)
    
    # Save Report
    report_file = f"{base_name}_spec.md"
    with open(report_file, "w") as f:
        f.write(report)
        
    logger.info(f"✅ Success! Artifacts generated:\n   - {img_name}.png\n   - {report_file}")

    
def process_directory(dir_path: str, model: str):
    logger.info(f"📂 Scanning directory: {dir_path}")
    
    # Extensions to look for
    valid_exts = {'.spss', '.sps', '.txt'} 
    
    processed_count = 0
    errors = []

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_exts:
                full_path = os.path.join(root, file)
                try:
                    print("-" * 40)
                    process_file(full_path, model)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to process {file}: {e}")
                    errors.append(file)

    print("=" * 40)
    logger.info(f"🏁 Batch Complete. Processed: {processed_count}. Errors: {len(errors)}")
    if errors:
        logger.info(f"⚠️ Failed files: {errors}")

def main():
    parser = argparse.ArgumentParser(description="Statify: Convert Legacy Code to Human Specs")
    parser.add_argument("path", help="Path to SPSS file or directory")
    parser.add_argument("--model", default="mistral:instruct", help="Ollama model to use")
    
    args = parser.parse_args()
    
    if os.path.isfile(args.path):
        process_file(args.path, args.model)
    elif os.path.isdir(args.path):
        process_directory(args.path, args.model)
    else:
        logger.error(f"Path not found: {args.path}")

if __name__ == "__main__":
    main()