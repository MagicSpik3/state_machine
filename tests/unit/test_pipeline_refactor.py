import pytest
from unittest.mock import MagicMock
from spss_engine.pipeline import CompilerPipeline
from spss_engine.parser import TokenType, ParsedCommand

class TestPipelineRefactor:
    """
    Verifies the new Dispatch Table architecture for the CompilerPipeline.
    Ensures that logic is correctly routed based on TokenType.
    """

    @pytest.fixture
    def pipeline(self):
        pipe = CompilerPipeline()
        # Mock internal components to isolate the routing logic
        pipe.parser = MagicMock()
        pipe.state_machine = MagicMock()
        pipe.extractor = MagicMock()
        return pipe

    def test_routing_assignment(self, pipeline):
        """Test that ASSIGNMENT tokens are routed to the handler in the dispatch table."""
        cmd = "COMPUTE x = 1."
        pipeline.parser.parse_command.return_value = ParsedCommand(TokenType.ASSIGNMENT, cmd)
        
        # 1. Create the Mock
        mock_handler = MagicMock()
        
        # 2. Inject it into the Dispatch Table (Crucial Step)
        # This simulates "If the table is configured correctly, does process() use it?"
        pipeline.dispatch_table[TokenType.ASSIGNMENT] = mock_handler
        
        # 3. Execute
        pipeline.process(cmd)
        
        # 4. Verify
        mock_handler.assert_called_once_with(cmd)

    def test_routing_conditional(self, pipeline):
        """Test that CONDITIONAL tokens trigger the configured handler."""
        cmd = "IF (x > 1) y = 2."
        pipeline.parser.parse_command.return_value = ParsedCommand(TokenType.CONDITIONAL, cmd)
        
        mock_handler = MagicMock()
        pipeline.dispatch_table[TokenType.CONDITIONAL] = mock_handler
        
        pipeline.process(cmd)
        mock_handler.assert_called_once_with(cmd)

    def test_routing_file_match(self, pipeline):
        """Test that FILE_MATCH tokens trigger the configured handler."""
        cmd = "MATCH FILES /FILE=*."
        pipeline.parser.parse_command.return_value = ParsedCommand(TokenType.FILE_MATCH, cmd)
        
        mock_handler = MagicMock()
        pipeline.dispatch_table[TokenType.FILE_MATCH] = mock_handler
        
        pipeline.process(cmd)
        mock_handler.assert_called_once_with(cmd)

    def test_routing_aggregate(self, pipeline):
        """Test that AGGREGATE tokens trigger the configured handler."""
        cmd = "AGGREGATE /OUTFILE=* /BREAK=ID /X=MEAN(Y)."
        pipeline.parser.parse_command.return_value = ParsedCommand(TokenType.AGGREGATE, cmd)
        
        mock_handler = MagicMock()
        pipeline.dispatch_table[TokenType.AGGREGATE] = mock_handler
        
        pipeline.process(cmd)
        mock_handler.assert_called_once_with(cmd)
            
    def test_routing_control_flow(self, pipeline):
        """Test that CONTROL_FLOW tokens trigger the configured handler."""
        cmd = "EXECUTE."
        pipeline.parser.parse_command.return_value = ParsedCommand(TokenType.CONTROL_FLOW, cmd)
        
        mock_handler = MagicMock()
        pipeline.dispatch_table[TokenType.CONTROL_FLOW] = mock_handler
        
        pipeline.process(cmd)
        mock_handler.assert_called_once_with(cmd)