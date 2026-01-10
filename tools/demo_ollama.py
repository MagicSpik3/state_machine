import sys
import logging
from spss_engine.pipeline import CompilerPipeline
from spec_writer.describer import SpecGenerator, OllamaClient

# Setup basic logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # 1. Define a "Real World" Logic Scenario
    code = """
    * Initialize Base Salary.
    COMPUTE Base_Salary = 50000.
    
    * Calculate Bonus (10% of Base).
    COMPUTE Bonus = Base_Salary * 0.10.
    
    * Calculate Total Compensation.
    COMPUTE Total_Comp = Base_Salary + Bonus.
    """

    print("🚀 1. Parsing SPSS Code...")
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # 2. Setup the LLM Client
    # We use 'mistral:instruct' as it fits your 6GB VRAM perfectly.
    model_name = "mistral:instruct" 
    print(f"🤖 2. Connecting to Ollama ({model_name})...")
    
    client = OllamaClient(model=model_name)
    
    # 3. Generate the Spec
    print("📝 3. Generating Business Specification (This may take a moment)...")
    generator = SpecGenerator(pipeline.state_machine, client)
    
    dead_vars = pipeline.analyze_dead_code()
    report = generator.generate_report(dead_ids=dead_vars)
    
    # 4. Output
    print("\n" + "="*40)
    print("FINAL GENERATED SPECIFICATION")
    print("="*40)
    print(report)
    print("="*40)

if __name__ == "__main__":
    main()