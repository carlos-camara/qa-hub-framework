"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        Pytest Configuration                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Shared fixtures and configuration for the test suite:                       ║
║  • Mock drivers (Selenium, Playwright)                                       ║
║  • Mock Behave contexts                                                       ║
║  • Temporary directories                                                      ║
║  • Test markers and plugins                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch
import tempfile
import os


# ═══════════════════════════════════════════════════════════════════════════════
# PYTEST MARKERS
# ═══════════════════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "elements: Element class tests")
    config.addinivalue_line("markers", "steps: Step definition tests")
    config.addinivalue_line("markers", "utils: Utility function tests")


# ═══════════════════════════════════════════════════════════════════════════════
# DRIVER FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_selenium_driver():
    """
    Create a mock Selenium WebDriver.
    
    Returns:
        MagicMock: Mock driver with common Selenium WebDriver methods.
        
    Example:
        def test_navigation(mock_selenium_driver):
            mock_selenium_driver.get("http://example.com")
            mock_selenium_driver.get.assert_called_once()
    """
    driver = MagicMock()
    driver.name = "selenium"
    driver.title = "Test Page"
    driver.current_url = "http://localhost:3000"
    driver.page_source = "<html><body>Test Content</body></html>"
    
    # Mock element findings
    mock_element = MagicMock()
    mock_element.text = "Element Text"
    mock_element.is_displayed.return_value = True
    mock_element.is_enabled.return_value = True
    mock_element.is_selected.return_value = False
    mock_element.get_attribute.return_value = "attribute_value"
    
    driver.find_element.return_value = mock_element
    driver.find_elements.return_value = [mock_element]
    
    return driver


@pytest.fixture
def mock_playwright_driver():
    """
    Create a mock Playwright driver wrapper.
    
    Returns:
        MagicMock: Mock driver with Playwright-compatible interface.
    """
    driver = MagicMock()
    driver.name = "playwright"
    driver.page = MagicMock()
    driver.browser = MagicMock()
    
    # Playwright page methods
    driver.page.title.return_value = "Test Page"
    driver.page.url = "http://localhost:3000"
    driver.page.content.return_value = "<html><body>Test</body></html>"
    
    # Playwright element
    mock_element = MagicMock()
    mock_element.text_content.return_value = "Element Text"
    mock_element.is_visible.return_value = True
    mock_element.is_enabled.return_value = True
    
    driver.page.query_selector.return_value = mock_element
    driver.page.query_selector_all.return_value = [mock_element]
    
    return driver


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_behave_context(mock_selenium_driver):
    """
    Create a mock Behave context with all common attributes.
    
    Returns:
        MagicMock: Mock context ready for step testing.
    """
    context = MagicMock()
    context.driver = mock_selenium_driver
    context.vars = {}
    context.response = MagicMock()
    context.response_json = {}
    
    # i18n handler
    context.i18n = MagicMock()
    context.i18n.resolve = lambda x: x
    
    # Variable handler
    context.variables = MagicMock()
    context.variables.resolve = lambda x: x
    
    # Visual config
    context.visual_config = {
        "baselines_dir": "/tmp/baselines",
        "fail": False,
        "threshold": 1.0
    }
    
    return context


@pytest.fixture
def mock_api_context(mock_behave_context):
    """
    Create a mock Behave context configured for API testing.
    
    Returns:
        MagicMock: Context with API response mocks.
    """
    context = mock_behave_context
    context.response.status_code = 200
    context.response.headers = {"Content-Type": "application/json"}
    context.response.text = '{"success": true}'
    context.response_json = {"success": True}
    context.base_url = "http://api.example.com"
    return context


@pytest.fixture
def mock_gui_context(mock_behave_context):
    """
    Create a mock Behave context configured for GUI testing.
    
    Returns:
        MagicMock: Context with GUI testing attributes.
    """
    context = mock_behave_context
    context.current_page = "dashboard"
    context.screenshots_dir = "/tmp/screenshots"
    context.page_objects = {}
    return context


# ═══════════════════════════════════════════════════════════════════════════════
# ELEMENT FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_web_element():
    """
    Create a mock Selenium WebElement.
    
    Returns:
        MagicMock: Mock element with common WebElement methods.
    """
    element = MagicMock()
    element.text = "Mock Element"
    element.tag_name = "div"
    element.is_displayed.return_value = True
    element.is_enabled.return_value = True
    element.is_selected.return_value = False
    element.get_attribute.return_value = None
    
    # Support for find_element within element
    nested_element = MagicMock()
    nested_element.text = "Nested Element"
    element.find_element.return_value = nested_element
    element.find_elements.return_value = [nested_element]
    
    return element


@pytest.fixture
def mock_select_options():
    """
    Create mock options for Select element testing.
    
    Returns:
        list: List of mock option elements.
    """
    options = []
    for i in range(3):
        opt = MagicMock()
        opt.text = f"Option {i + 1}"
        opt.get_attribute.return_value = f"option_{i + 1}"
        opt.is_selected.return_value = (i == 0)  # First option selected
        options.append(opt)
    return options


# ═══════════════════════════════════════════════════════════════════════════════
# FILE SYSTEM FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_test_dir(tmp_path):
    """
    Create a temporary directory structure for testing.
    
    Returns:
        dict: Paths to various temporary directories.
    """
    dirs = {
        "root": tmp_path,
        "baselines": tmp_path / "baselines",
        "screenshots": tmp_path / "screenshots",
        "reports": tmp_path / "reports",
        "page_objects": tmp_path / "page_objects"
    }
    
    for path in dirs.values():
        if isinstance(path, type(tmp_path)):
            path.mkdir(exist_ok=True)
    
    return dirs


@pytest.fixture
def sample_yaml_page_object(temp_test_dir):
    """
    Create a sample YAML page object file.
    
    Returns:
        str: Path to the created YAML file.
    """
    yaml_content = """
dashboard:
  header:
    by: css
    value: .header-title
    type: text
  login_button:
    by: id
    value: login-btn
    type: button
  username_input:
    by: id
    value: username
    type: input
  remember_me:
    by: id
    value: remember-checkbox
    type: checkbox
  country_select:
    by: id
    value: country
    type: select
"""
    yaml_path = temp_test_dir["page_objects"] / "dashboard.yml"
    yaml_path.write_text(yaml_content)
    return str(yaml_path)


# ═══════════════════════════════════════════════════════════════════════════════
# API RESPONSE FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_api_responses():
    """
    Sample API responses for testing.
    
    Returns:
        dict: Various sample API response payloads.
    """
    return {
        "user": {
            "id": 12345,
            "name": "Carlos",
            "email": "carlos@example.com",
            "roles": ["admin", "user"],
            "profile": {
                "avatar": "https://example.com/avatar.jpg",
                "bio": "Test user"
            }
        },
        "list": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ],
        "empty": {},
        "error": {
            "code": "NOT_FOUND",
            "message": "Resource not found"
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def assert_element_visible():
    """
    Helper fixture for asserting element visibility.
    
    Returns:
        callable: Function to assert element visibility.
    """
    def _assert(element, message="Element should be visible"):
        assert element.is_displayed(), message
    return _assert
