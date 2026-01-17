import pytest
from spss_engine.state import StateMachine
from spss_engine.events import FileReadEvent
from code_forge.generator import RGenerator

class TestRCodegen:
    def test_generate_strict_loader(self):
        """
        Verify that we generate type-safe loading code when a Schema is present.
        """
        # 1. Setup State with Schema
        state = StateMachine()
        state.register_input(
            filename="input_people.csv",
            fmt="CSV",
            delimiter=",",
            raw_vars=[("id", "F8.0")] # This triggers the type enforcement
        )
        
        generator = RGenerator(state)
        
        # 2. Mock Event (Legacy support for the method signature)
        event = FileReadEvent(
            source_command="GET DATA...", 
            filename="input_people.csv",
            variables=[("id", "F8.0")]
        )
        
        # 3. Generate Snippet
        code = generator.generate_loader_snippet(event)
        
        # 4. Assertions
        assert 'df <- read.csv' in code       
        # 🟢 CHANGED: Expect single quotes as per Generator implementation
        assert "file = 'input_people.csv'" in code
        assert 'df$id <- as.numeric(df$id)' in code