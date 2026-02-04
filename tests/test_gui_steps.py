"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                         GUI Steps Unit Tests                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for GUI step definitions including:                                   ║
║  • Navigation steps         • Text verification                              ║
║  • Page title validation    • Token resolution                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_context():
    """Create a mock Behave context with common attributes."""
    context = MagicMock()
    context.driver = MagicMock()
    context.i18n = MagicMock()
    context.i18n.resolve = lambda x: x  # Pass-through by default
    context.variables = MagicMock()
    context.variables.resolve = lambda x: x  # Pass-through by default
    return context


@pytest.fixture
def mock_body_element():
    """Create a mock body element for text searches."""
    element = MagicMock()
    element.text = "Welcome to the Dashboard. Please login to continue."
    return element


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: NAVIGATION STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class TestNavigationSteps:
    """Tests for browser navigation step definitions."""

    def test_navigate_to_url(self, mock_context):
        """✓ Navigate step calls driver.get() with correct URL."""
        from qa_framework.steps.gui_steps import step_navigate_to_url
        
        step_navigate_to_url(mock_context, "http://test.com")
        
        mock_context.driver.get.assert_called_once_with("http://test.com")

    def test_navigate_to_dashboard(self, mock_context):
        """✓ Dashboard navigation step uses correct URL."""
        from qa_framework.steps.gui_steps import step_navigate_to_dashboard
        
        step_navigate_to_dashboard(mock_context, "http://localhost:3000/dashboard/")
        
        mock_context.driver.get.assert_called_once_with("http://localhost:3000/dashboard/")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: TEXT VERIFICATION STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTextVerificationSteps:
    """Tests for text verification step definitions."""

    def test_verify_text_present_success(self, mock_context, mock_body_element):
        """✓ Text verification passes when text is found."""
        from qa_framework.steps.gui_steps import step_verify_text_present
        
        mock_context.driver.find_element.return_value = mock_body_element
        
        # Should not raise
        step_verify_text_present(mock_context, "Welcome")

    def test_verify_text_present_case_insensitive(self, mock_context, mock_body_element):
        """✓ Text verification is case-insensitive."""
        from qa_framework.steps.gui_steps import step_verify_text_present
        
        mock_context.driver.find_element.return_value = mock_body_element
        
        # Should not raise - case insensitive match
        step_verify_text_present(mock_context, "WELCOME")
        step_verify_text_present(mock_context, "dashboard")

    def test_verify_text_present_fails_when_not_found(self, mock_context):
        """✓ Text verification fails when text is not found."""
        from qa_framework.steps.gui_steps import step_verify_text_present
        
        mock_body = MagicMock()
        mock_body.text = "Error page - Something went wrong"
        mock_context.driver.find_element.return_value = mock_body
        
        with pytest.raises(AssertionError):
            step_verify_text_present(mock_context, "Welcome back")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: PAGE TITLE STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPageTitleSteps:
    """Tests for page title verification step definitions."""

    @patch("qa_framework.steps.gui_steps.wait_for_title")
    def test_verify_page_title_success(self, mock_wait, mock_context):
        """✓ Title verification passes when title matches."""
        from qa_framework.steps.gui_steps import step_verify_page_title
        
        mock_context.driver.title = "Home Page"
        
        step_verify_page_title(mock_context, "Home Page")
        
        mock_wait.assert_called_once()

    @patch("qa_framework.steps.gui_steps.wait_for_title")
    def test_verify_page_title_with_i18n(self, mock_wait, mock_context):
        """✓ Title verification supports i18n token resolution."""
        from qa_framework.steps.gui_steps import step_verify_page_title
        
        # Setup i18n to resolve tokens
        mock_context.i18n.resolve = lambda x: "Dashboard Principal"
        mock_context.driver.title = "Dashboard Principal"
        
        step_verify_page_title(mock_context, "[LANG:dashboard.title]")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: WAIT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestWaitUtilities:
    """Tests for driver-agnostic wait utility functions."""

    def test_wait_for_visible_selenium(self, mock_context):
        """✓ wait_for_visible works with Selenium drivers."""
        from qa_framework.steps.gui_steps import wait_for_visible
        
        # Ensure driver doesn't have 'page' (not Playwright)
        del mock_context.driver.page
        
        locator = (By.ID, "element-id")
        
        # Should not raise
        with patch("qa_framework.steps.gui_steps.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = MagicMock()
            wait_for_visible(mock_context.driver, locator, timeout=10)
            mock_wait.assert_called_once()

    def test_wait_for_clickable_selenium(self, mock_context):
        """✓ wait_for_clickable works with Selenium drivers."""
        from qa_framework.steps.gui_steps import wait_for_clickable
        
        # Ensure driver doesn't have 'page' (not Playwright)
        del mock_context.driver.page
        
        locator = (By.CSS_SELECTOR, ".btn-primary")
        
        with patch("qa_framework.steps.gui_steps.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = MagicMock()
            wait_for_clickable(mock_context.driver, locator, timeout=5)
            mock_wait.assert_called_once()

    def test_wait_for_visible_playwright(self):
        """✓ wait_for_visible works with Playwright drivers."""
        from qa_framework.steps.gui_steps import wait_for_visible
        
        # Setup Playwright-like driver
        mock_driver = MagicMock()
        mock_driver.page = MagicMock()
        mock_driver._convert_locator = lambda by, val: f"#{val}"
        
        locator = (By.ID, "element-id")
        wait_for_visible(mock_driver, locator, timeout=10)
        
        mock_driver.page.wait_for_selector.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: TOKEN RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestTokenResolution:
    """Tests for token resolution in step definitions."""

    def test_resolve_tokens_with_variables(self, mock_context):
        """✓ resolve_tokens handles variable tokens."""
        from qa_framework.steps.gui_steps import resolve_tokens
        
        mock_context.variables.resolve = lambda x: x.replace("[UUID]", "abc-123")
        
        result = resolve_tokens(mock_context, "User ID: [UUID]")
        assert result == "User ID: abc-123"

    def test_resolve_tokens_with_i18n(self, mock_context):
        """✓ resolve_tokens handles i18n tokens."""
        from qa_framework.steps.gui_steps import resolve_tokens
        
        mock_context.i18n.resolve = lambda x: x.replace("[LANG:greeting]", "Hello")
        
        result = resolve_tokens(mock_context, "[LANG:greeting] World")
        assert result == "Hello World"

    def test_resolve_tokens_passthrough(self, mock_context):
        """✓ resolve_tokens returns plain text unchanged."""
        from qa_framework.steps.gui_steps import resolve_tokens
        
        result = resolve_tokens(mock_context, "Plain text without tokens")
        assert result == "Plain text without tokens"

    def test_resolve_tokens_non_string(self, mock_context):
        """✓ resolve_tokens returns non-strings unchanged."""
        from qa_framework.steps.gui_steps import resolve_tokens
        
        assert resolve_tokens(mock_context, 123) == 123
        assert resolve_tokens(mock_context, None) is None
        assert resolve_tokens(mock_context, True) is True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: SCREENSHOT STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class TestScreenshotSteps:
    """Tests for screenshot capture step definitions."""

    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    def test_take_screenshot(self, mock_makedirs, mock_exists, mock_context):
        """✓ Screenshot step saves file to correct location."""
        from qa_framework.steps.gui_steps import step_take_screenshot
        
        mock_context.screenshots_dir = "screenshots"
        # Remove 'embed' attribute to prevent file reading attempt
        del mock_context.embed
        
        step_take_screenshot(mock_context, "login_page")
        
        mock_context.driver.save_screenshot.assert_called_once()
        # Verify the filename contains the expected name
        call_args = mock_context.driver.save_screenshot.call_args[0][0]
        assert "login_page.png" in call_args


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: CURRENT PAGE CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

class TestCurrentPageContext:
    """Tests for context-aware step definitions."""

    def test_set_current_page(self, mock_context):
        """✓ Setting current page stores value in context."""
        from qa_framework.steps.gui_steps import step_set_current_page
        
        # Patch file operations to avoid YAML loading
        with patch("os.path.join", return_value="/fake/path"):
            with patch("qa_framework.steps.gui_steps._find_page_yaml", return_value=None):
                step_set_current_page(mock_context, "dashboard")
        
        assert mock_context.current_page == "dashboard"

    def test_click_without_current_page(self, mock_context):
        """✓ Context-aware click raises error without current_page."""
        from qa_framework.steps.gui_steps import step_click_current_page_object
        
        mock_context.current_page = None
        
        with pytest.raises(AttributeError, match="No current page set"):
            step_click_current_page_object(mock_context, "submit_button")


# ═══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
