from spss_engine.pipeline import CompilerPipeline
from spec_writer.graph import GraphGenerator

def main():
    # Scenario: 'temp' is calculated but never used. 'x' is overwritten.
    code = """
    * 1. Create a variable that is never used (Zombie).
    COMPUTE temp = 999.
    
    * 2. Initialize X.
    COMPUTE x = 10.
    
    * 3. Overwrite X without reading X_0 (Zombie).
    COMPUTE x = 20.
    
    * 4. Use X (Keeps X_1 alive).
    COMPUTE y = x + 5.
    """
    
    print("🚀 Hunting Zombies...")
    pipeline = CompilerPipeline()
    pipeline.process(code)
    
    # Analyze
    dead_vars = pipeline.analyze_dead_code()
    print(f"💀 Dead Code Detected: {dead_vars}")
    
    # Render
    filename = "zombie_attack"
    print(f"🎨 Painting {filename}.png...")
    
    path = GraphGenerator.render(
        pipeline.state_machine, 
        filename=filename, 
        highlight_dead=dead_vars
    )
    print(f"✅ Saved to {path}")

if __name__ == "__main__":
    main()