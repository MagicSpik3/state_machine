import pytest
from spss_engine.state import StateMachine, InputSchema, ColumnSchema

class TestDataContract:
    """
    Verifies that the State Machine correctly stores and organizes 
    data loading contracts (Schemas) separate from logic nodes.
    """

    def test_register_simple_input(self):
        """
        Scenario: A simple CSV load with no specific variable types.
        """
        state = StateMachine()
        state.register_input(
            filename="data.csv",
            fmt="CSV",
            delimiter=",",
            raw_vars=[] # No explicit variables defined
        )

        assert len(state.inputs) == 1
        schema = state.inputs[0]
        assert schema.filename == "data.csv"
        assert schema.format == "CSV"
        assert schema.delimiter == ","
        assert schema.columns == []

    def test_register_input_with_schema(self):
        """
        Scenario: GET DATA with specific column definitions (F8.0, A10).
        Goal: Ensure SPSS types are mapped to Generic types.
        """
        state = StateMachine()
        
        # Raw variables from the Parser event
        raw_vars = [
            ("id", "F8.0"),       # Numeric
            ("gender", "A1"),     # String
            ("start_date", "ADATE10") # Date
        ]

        state.register_input(
            filename="people.txt",
            fmt="CSV",
            delimiter="\t",
            raw_vars=raw_vars
        )

        schema = state.inputs[0]
        assert len(schema.columns) == 3
        
        # Check ID (Numeric)
        col_id = schema.columns[0]
        assert col_id.name == "id"
        assert col_id.type_generic == "Numeric"
        assert col_id.type_specific == "F8.0"

        # Check Gender (String)
        col_gender = schema.columns[1]
        assert col_gender.name == "gender"
        assert col_gender.type_generic == "String"
        assert col_gender.type_specific == "A1"

        # Check Date (Date)
        col_date = schema.columns[2]
        assert col_date.name == "start_date"
        assert col_date.type_generic == "Date"

    def test_schema_description(self):
        """Ensure the schema can describe itself textually."""
        state = StateMachine()
        state.register_input("test.sav", "SAV", None, [])
        
        desc = state.inputs[0].describe()
        assert "Dataset 'test.sav'" in desc
        assert "(SAV)" in desc