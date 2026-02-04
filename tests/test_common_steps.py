"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        Common Steps Unit Tests                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for common utility steps including:                                   ║
║  • Explicit timing control                                                   ║
║  • Variable storage from elements                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.vars = {}
    return context

def test_wait_seconds(mock_context):
    from qa_framework.steps.common_steps import step_wait_seconds
    with patch("time.sleep") as mock_sleep:
        step_wait_seconds(mock_context, 5)
        mock_sleep.assert_called_once_with(5.0)

@patch("qa_framework.steps.gui_steps.get_element_from_page_object")
def test_store_element_text(mock_get_elem, mock_context):
    from qa_framework.steps.common_steps import step_store_element_text
    mock_elem = MagicMock()
    mock_elem.get_text.return_value = "ORD-12345"
    mock_get_elem.return_value = mock_elem
    
    step_store_element_text(mock_context, "order_id", "MyID")
    
    assert mock_context.vars["MyID"] == "ORD-12345"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
