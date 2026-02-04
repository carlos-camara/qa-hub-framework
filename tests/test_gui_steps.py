"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                         GUI Steps Unit Tests                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for GUI step definitions including:                                   ║
║  • Navigation & Windows      • Mouse & Keyboard Actions                      ║
║  • Attributes & Iframes      • Transitions & Contexts                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.driver = MagicMock()
    context.driver.window_handles = ["handle1", "handle2"]
    context.driver.current_window_handle = "handle1"
    context.i18n = MagicMock()
    context.i18n.resolve = lambda x: x
    context.variables = MagicMock()
    context.variables.resolve = lambda x: x
    context.current_page = "test_page"
    return context

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: INTERACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInteractionSteps:
    """Tests for mouse and keyboard interactions."""

    @patch("qa_framework.steps.gui_steps.get_element_from_page_object")
    @patch("selenium.webdriver.common.action_chains.ActionChains")
    def test_hover_step(self, mock_actions_class, mock_get_elem, mock_context):
        from qa_framework.steps.gui_steps import step_hover_over_element
        mock_elem = MagicMock()
        mock_get_elem.return_value = mock_elem
        
        # Configure chaining
        instance = mock_actions_class.return_value
        instance.move_to_element.return_value = instance
        
        step_hover_over_element(mock_context, "target_elem")
        
        mock_elem.wait_until_visible.assert_called_once()
        instance.move_to_element.assert_called()
        instance.perform.assert_called()

    @patch("qa_framework.steps.gui_steps.get_element_from_page_object")
    @patch("selenium.webdriver.common.action_chains.ActionChains")
    def test_double_click_step(self, mock_actions_class, mock_get_elem, mock_context):
        from qa_framework.steps.gui_steps import step_double_click_element
        mock_elem = MagicMock()
        mock_get_elem.return_value = mock_elem
        
        # Configure chaining
        instance = mock_actions_class.return_value
        instance.double_click.return_value = instance
        
        step_double_click_element(mock_context, "target_elem")
        
        mock_elem.wait_until_clickable.assert_called_once()
        instance.double_click.assert_called()
        instance.perform.assert_called()

    @patch("selenium.webdriver.common.action_chains.ActionChains")
    def test_press_key_step(self, mock_actions_class, mock_context):
        from qa_framework.steps.gui_steps import step_press_key
        
        # Configure chaining
        instance = mock_actions_class.return_value
        instance.send_keys.return_value = instance
        
        step_press_key(mock_context, "Enter")
        instance.send_keys.assert_called()
        instance.perform.assert_called()

    def test_press_key_invalid(self, mock_context):
        from qa_framework.steps.gui_steps import step_press_key
        with pytest.raises(ValueError, match="Unsupported key"):
            step_press_key(mock_context, "InvalidKey")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: WINDOW & FRAME TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestContextSwitching:
    """Tests for tab and iframe switching."""

    def test_switch_tab(self, mock_context):
        from qa_framework.steps.gui_steps import step_switch_to_next_tab
        step_switch_to_next_tab(mock_context)
        mock_context.driver.switch_to.window.assert_called_with("handle2")

    def test_close_tab(self, mock_context):
        from qa_framework.steps.gui_steps import step_close_current_tab
        step_close_current_tab(mock_context)
        mock_context.driver.close.assert_called_once()
        mock_context.driver.switch_to.window.assert_called_with("handle1")

    @patch("qa_framework.steps.gui_steps.get_element_from_page_object")
    def test_switch_to_iframe(self, mock_get_elem, mock_context):
        from qa_framework.steps.gui_steps import step_switch_to_iframe
        mock_elem = MagicMock()
        mock_get_elem.return_value = mock_elem
        
        step_switch_to_iframe(mock_context, "my_frame")
        mock_context.driver.switch_to.frame.assert_called_once()

    def test_switch_to_default(self, mock_context):
        from qa_framework.steps.gui_steps import step_switch_to_default_content
        step_switch_to_default_content(mock_context)
        mock_context.driver.switch_to.default_content.assert_called_once()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: ATTRIBUTE & URL VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdvancedValidation:
    """Tests for attribute and URL verification."""

    @patch("qa_framework.steps.gui_steps.get_element_from_page_object")
    def test_verify_attribute(self, mock_get_elem, mock_context):
        from qa_framework.steps.gui_steps import step_verify_attribute
        mock_elem = MagicMock()
        mock_elem.get_attribute.return_value = "submit"
        mock_get_elem.return_value = mock_elem
        
        step_verify_attribute(mock_context, "btn", "type", "submit")

    @patch("qa_framework.steps.gui_steps.get_element_from_page_object")
    def test_verify_attribute_fails(self, mock_get_elem, mock_context):
        from qa_framework.steps.gui_steps import step_verify_attribute
        mock_elem = MagicMock()
        mock_elem.get_attribute.return_value = "button"
        mock_get_elem.return_value = mock_elem
        
        with pytest.raises(AssertionError, match="Expected attribute"):
            step_verify_attribute(mock_context, "btn", "type", "submit")

    def test_verify_url_contains(self, mock_context):
        from qa_framework.steps.gui_steps import step_verify_url_contains
        mock_context.driver.current_url = "https://example.com/login?token=123"
        
        step_verify_url_contains(mock_context, "login")

    @patch("qa_framework.steps.gui_steps.get_element_from_page_object")
    def test_verify_hidden(self, mock_get_elem, mock_context):
        from qa_framework.steps.gui_steps import step_verify_element_hidden
        mock_elem = MagicMock()
        mock_elem.is_displayed.return_value = False
        mock_get_elem.return_value = mock_elem
        
        step_verify_element_hidden(mock_context, "ghost_elem")

    @patch("qa_framework.steps.gui_steps.get_element_from_page_object")
    def test_verify_hidden_not_present(self, mock_get_elem, mock_context):
        from qa_framework.steps.gui_steps import step_verify_element_hidden
        mock_get_elem.side_effect = NoSuchElementException("Element not found")
        
        # Should pass even if element doesn't exist
        step_verify_element_hidden(mock_context, "deleted_elem")

# ═══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
