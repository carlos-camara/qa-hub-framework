"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        Logger Utility Unit Tests                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for ContextualLogger including:                                        ║
║  • Log levels (Info, Success, Warning, Error, Debug)                          ║
║  • Context extraction from Behave objects                                     ║
║  • Output formatting and colors                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from qa_framework.utils.logger import ContextualLogger, Colors

@pytest.fixture
def mock_context():
    """Create a mock Behave context with feature and scenario."""
    context = MagicMock()
    context.feature.name = "Billing"
    context.scenario.name = "Process Invoice"
    return context

def test_get_timestamp():
    """✓ Timestamp should follow HH:MM:SS format."""
    ts = ContextualLogger._get_timestamp()
    assert len(ts) == 8 # HH:MM:SS
    assert ":" in ts

def test_get_context_info_no_context():
    """✓ Should return empty string when context is None."""
    info = ContextualLogger._get_context_info(None)
    assert info == ""

def test_get_context_info_with_context(mock_context):
    """✓ Should extract feature and scenario names."""
    info = ContextualLogger._get_context_info(mock_context)
    assert "Billing" in info
    assert "Process Invoice" in info
    assert Colors.GRAY in info

@patch("builtins.print")
def test_info_log(mock_print, mock_context):
    """✓ Info log should contain blue color codes."""
    ContextualLogger.info("Testing INFO", mock_context)
    args, _ = mock_print.call_args
    output = args[0]
    assert "INFO:" in output
    assert Colors.BLUE in output
    assert "Testing INFO" in output

@patch("builtins.print")
def test_success_log(mock_print, mock_context):
    """✓ Success log should contain green color codes."""
    ContextualLogger.success("Testing SUCCESS", mock_context)
    args, _ = mock_print.call_args
    output = args[0]
    assert "SUCCESS:" in output
    assert Colors.GREEN in output

@patch("builtins.print")
def test_warning_log(mock_print, mock_context):
    """✓ Warning log should contain yellow color codes."""
    ContextualLogger.warning("Testing WARNING", mock_context)
    args, _ = mock_print.call_args
    output = args[0]
    assert "WARNING:" in output
    assert Colors.YELLOW in output

@patch("builtins.print")
def test_error_log(mock_print, mock_context):
    """✓ Error log should go to stderr and contain red color codes."""
    ContextualLogger.error("Testing ERROR", mock_context)
    args, kwargs = mock_print.call_args
    output = args[0]
    assert "ERROR:" in output
    assert Colors.RED in output
    assert kwargs["file"] == sys.stderr

@patch("builtins.print")
def test_section_log(mock_print):
    """✓ Section log should be bold and underlined."""
    ContextualLogger.section("new section")
    args, _ = mock_print.call_args
    output = args[0]
    assert "NEW SECTION" in output
    assert Colors.BOLD in output
    assert Colors.UNDERLINE in output

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
