import os
from spss_engine.pipeline import CompilerPipeline
from spss_engine.graph import GraphGenerator

def main():
    # 1. Define the "Nightmare" Code (Control Flow Coupling)
    code = """
    * Phase 1: Set Control Flag to 2 (Even Mode).
    COMPUTE x = 2.
    
    * Logic Block A.
    IF (x = 2) COMPUTE Result_A = 100.
    
    * Phase 2: Reuse Control Flag (Set to 3).
    COMPUTE x = 3.
    
    * Logic Block B.
    IF (x = 3) COMPUTE Result_B = 200.
    """
    
    print("🚀 Processing SPSS Code...")
    
    # 2. Run Pipeline
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # 3. Render Graph
    output_filename = "flag_variable_flow"
    print(f"🎨 Rendering graph to {output_filename}.png...")
    
    # Access the state machine directly from the pipeline to pass to the generator
    # (We might want to expose a helper for this later, but this works for now)
    output_path = GraphGenerator.render(
        pipeline.state_machine, 
        filename=output_filename, 
        format="png"
    )
    
    print(f"✅ Done! Graph saved to:\n{output_path}")

if __name__ == "__main__":
    main()