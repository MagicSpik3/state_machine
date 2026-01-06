import os
from spss_engine.pipeline import CompilerPipeline
from spec_writer.graph import GraphGenerator

def main():
    # 1. Define the Payroll Logic
    # This involves multiple variables interacting, unlike the single 'x' toggle.
    code = """
    * Init Variables.
    COMPUTE Gross = 50000.
    COMPUTE Rate = 0.2.
    
    * Calculate Tax (Depends on Gross and Rate).
    COMPUTE Tax = Gross * Rate.
    
    * Calculate Net Pay (Depends on Gross and Tax).
    COMPUTE Net = Gross - Tax.
    """
    
    print("🚀 Processing Payroll Logic...")
    
    # 2. Run Pipeline
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # 3. Render Graph
    output_filename = "payroll_flow"
    print(f"🎨 Rendering graph to {output_filename}.png...")
    
    output_path = GraphGenerator.render(
        pipeline.state_machine, 
        filename=output_filename, 
        format="png"
    )
    
    print(f"✅ Done! Graph saved to:\n{output_path}")

if __name__ == "__main__":
    main()