import pytest
from spss_engine.state import ColumnSchema, InputSchema

class TestSchemaDefinitions:
    """
    Strictly tests the Data Contract data structures in state.py
    """

    def test_column_schema_structure(self):
        """Verify ColumnSchema stores type info correctly."""
        col = ColumnSchema(name="age", type_generic="Numeric", type_specific="F8.0")
        assert col.name == "age"
        assert col.type_generic == "Numeric"
        assert col.type_specific == "F8.0"

    def test_input_schema_describe_csv(self):
        """Verify InputSchema describes a CSV correctly."""
        cols = [
            ColumnSchema("id", "Numeric", "F8.0"),
            ColumnSchema("name", "String", "A20")
        ]
        schema = InputSchema(
            filename="data.csv", 
            format="CSV", 
            columns=cols, 
            delimiter=","
        )
        
        description = schema.describe()
        assert "Dataset 'data.csv'" in description
        assert "(CSV)" in description
        assert "2 columns" in description

    def test_input_schema_describe_sav(self):
        """Verify InputSchema describes a SAV file (no delimiter)."""
        schema = InputSchema(
            filename="data.sav", 
            format="SAV", 
            columns=[], 
            delimiter=None
        )
        
        description = schema.describe()
        assert "Dataset 'data.sav'" in description
        assert "(SAV)" in description
        assert "0 columns" in description