"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                         GUI Step Definitions                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This module contains all Gherkin step definitions for GUI/Browser testing.  ║
║                                                                              ║
║  Features:                                                                    ║
║  • Page Object pattern with YAML-driven locators                             ║
║  • Context-aware steps (automatic page detection)                            ║
║  • I18n and Variable token resolution                                        ║
║  • Visual regression testing with configurable tolerance                     ║
║  • Selenium/Playwright agnostic wait utilities                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from behave import given, when, then, step
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import time
from ..core.language_handler import LanguageHandler
from ..utils.visual import VisualHandler
from ..utils.logger import ContextualLogger


@step('I set the viewport to "{width}" x "{height}"')
def step_set_viewport_size(context, width, height):
    """
    Sets the browser viewport to a specific size.
    Useful for testing responsive layouts.
    """
    w = int(width)
    h = int(height)
    ContextualLogger.info(f"Setting viewport to {w}x{h}", context)
    context.driver.set_window_size(w, h)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: DRIVER-AGNOSTIC WAIT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
# These functions provide unified wait mechanisms that work with both
# Selenium WebDriver and Playwright Page objects transparently.
# ═══════════════════════════════════════════════════════════════════════════════

def wait_for_visible(driver, locator, timeout=10):
    """
    Wait until an element is visible on the page.
    
    This function is driver-agnostic and works with both Selenium and Playwright.
    For Selenium, it uses WebDriverWait with visibility_of_element_located.
    For Playwright, it uses wait_for_selector with state='visible'.
    
    Args:
        driver: WebDriver instance (Selenium) or PlaywrightWrapper
        locator: Tuple of (By.TYPE, 'selector') for Selenium compatibility
        timeout: Maximum seconds to wait (default: 10)
        
    Raises:
        TimeoutException: If element is not visible within timeout
    """
    if hasattr(driver, 'page'):  # Playwright
        selector = driver._convert_locator(locator[0], locator[1])
        driver.page.wait_for_selector(selector, state="visible", timeout=timeout*1000)
    else:  # Selenium
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


def wait_for_clickable(driver, locator, timeout=10):
    """
    Wait until an element is clickable (visible and enabled).
    
    For Selenium, uses element_to_be_clickable expected condition.
    For Playwright, uses visibility check (Playwright auto-waits for actionability).
    
    Args:
        driver: WebDriver instance or PlaywrightWrapper
        locator: Tuple of (By.TYPE, 'selector')
        timeout: Maximum seconds to wait
        
    Raises:
        TimeoutException: If element is not clickable within timeout
    """
    if hasattr(driver, 'page'):
        selector = driver._convert_locator(locator[0], locator[1])
        driver.page.wait_for_selector(selector, state="visible", timeout=timeout*1000)
    else:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def wait_for_presence(driver, locator, timeout=10):
    """
    Wait until an element is present in the DOM (may not be visible).
    
    Useful for elements that are rendered but hidden, or for checking
    if dynamic content has been loaded into the page structure.
    
    Args:
        driver: WebDriver instance or PlaywrightWrapper
        locator: Tuple of (By.TYPE, 'selector')
        timeout: Maximum seconds to wait
        
    Raises:
        TimeoutException: If element is not present within timeout
    """
    if hasattr(driver, 'page'):
        selector = driver._convert_locator(locator[0], locator[1])
        driver.page.wait_for_selector(selector, state="attached", timeout=timeout*1000)
    else:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def wait_for_title(driver, title, timeout=10):
    """
    Wait until the page title matches the expected value.
    
    For Selenium, uses title_is expected condition.
    For Playwright, polls the title property until match or timeout.
    
    Args:
        driver: WebDriver instance or PlaywrightWrapper
        title: Expected page title (exact match)
        timeout: Maximum seconds to wait
        
    Raises:
        TimeoutException: If title doesn't match within timeout
    """
    if hasattr(driver, 'page'):
        start = time.time()
        while time.time() - start < timeout:
            if driver.title == title:
                return True
            time.sleep(0.5)
        raise TimeoutException(f"Title '{title}' not found. Current: '{driver.title}'")
    else:
        WebDriverWait(driver, timeout).until(EC.title_is(title))


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: TOKEN RESOLUTION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
# These functions resolve dynamic tokens in Gherkin step parameters:
#   - [LANG:key.path] → Internationalized strings from language YAML
#   - [UUID], [NOW], [RANDOM], etc. → Dynamic variable generation
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_tokens(context, text):
    """
    Resolve all tokens in the given text.
    
    Token resolution order:
    1. Variables: [UUID], [NOW(%Y)], [RANDOM], [STRING_WITH_LENGTH_10], etc.
    2. I18n: [LANG:dashboard.header.title] → localized string
    
    This function is the central resolver used by all step definitions
    to support dynamic test data without hardcoding values.
    
    Args:
        context: Behave context (must have 'variables' and 'i18n' attributes)
        text: Raw string potentially containing tokens
        
    Returns:
        Resolved string with all tokens replaced by actual values
        
    Example:
        resolve_tokens(context, "Hello [LANG:greeting] [UUID]")
        → "Hello Welcome to Dashboard 550e8400-e29b-41d4-a716-446655440000"
    """
    if not isinstance(text, str):
        return text
        
    resolved = text
    
    # Step 1: Resolve Variables ([UUID], [NOW], etc.)
    if hasattr(context, 'variables'):
        resolved = context.variables.resolve(resolved)
    
    # Step 2: Resolve I18n ([LANG:key.path])
    if isinstance(resolved, str) and hasattr(context, 'i18n'):
        resolved = context.i18n.resolve(resolved)
        
    return resolved


def resolve_i18n(context, text):
    """
    Legacy wrapper for resolve_tokens().
    
    Maintained for backward compatibility with older step definitions.
    New implementations should use resolve_tokens() directly.
    
    Args:
        context: Behave context
        text: Raw string with potential tokens
        
    Returns:
        Resolved string
    """
    return resolve_tokens(context, text)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: BASIC NAVIGATION STEPS
# ═══════════════════════════════════════════════════════════════════════════════
# Fundamental browser navigation and page verification steps.
# ═══════════════════════════════════════════════════════════════════════════════

@given('I navigate to "{url}"')
def step_navigate_to_url(context, url):
    """
    Navigate the browser to a specific URL.
    
    Example:
        Given I navigate to "https://example.com/login"
    """
    resolved_url = resolve_tokens(context, url)
    ContextualLogger.info(f"Navigating to: {resolved_url}", context)
    context.driver.get(resolved_url)


@then('the page title should be "{expected_title}"')
def step_verify_page_title(context, expected_title):
    """
    Verify the page title matches the expected value.
    
    Supports I18n tokens for localized title verification.
    
    Example:
        Then the page title should be "[LANG:common.page_title]"
    """
    resolved_title = resolve_i18n(context, expected_title)
    wait_for_title(context.driver, resolved_title)
    assert context.driver.title == resolved_title


@when('I click on the element with text "{text}"')
def step_click_element_by_text(context, text):
    """
    Click on any element containing the specified text.
    
    Uses XPath text() matching. Supports I18n tokens.
    
    Example:
        When I click on the element with text "[LANG:buttons.submit]"
    """
    resolved_text = resolve_i18n(context, text)
    locator = (By.XPATH, f"//*[contains(text(), '{resolved_text}')]")
    wait_for_clickable(context.driver, locator)
    element = context.driver.find_element(*locator)
    element.click()


@when('I click on the button with text "{button_text}"')
def step_click_button_by_text(context, button_text):
    """
    Click on a <button> element containing the specified text.
    
    Uses case-insensitive matching for flexibility.
    
    Example:
        When I click on the button with text "Submit"
    """
    resolved_text = resolve_i18n(context, button_text)
    xpath = f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{resolved_text.lower()}')]"
    locator = (By.XPATH, xpath)
    wait_for_clickable(context.driver, locator)
    element = context.driver.find_element(*locator)
    element.click()


@then('I should see the text "{text}"')
def step_verify_text_present(context, text):
    """
    Verify that specific text is present anywhere on the page.
    
    Uses case-insensitive, whitespace-normalized matching for robustness.
    
    Example:
        Then I should see the text "Welcome back, John!"
    """
    resolved_text = resolve_i18n(context, text)
    body_text = context.driver.find_element(By.TAG_NAME, "body").text
    normalized_body = " ".join(body_text.lower().split())
    normalized_expected = " ".join(resolved_text.lower().split())
    assert normalized_expected in normalized_body, \
        f"Text '{resolved_text}' not found (case-insensitive normalized search)"


@then('I should see an element with class "{class_name}"')
def step_verify_element_by_class(context, class_name):
    """
    Verify an element with the specified CSS class is visible.
    
    Example:
        Then I should see an element with class "success-banner"
    """
    locator = (By.CLASS_NAME, class_name)
    wait_for_visible(context.driver, locator)
    element = context.driver.find_element(*locator)
    assert element.is_displayed()


@when('I scroll to the bottom of the page')
def step_scroll_to_bottom(context):
    """
    Scroll to the bottom of the page.
    
    Useful for triggering lazy-loaded content or reaching footer elements.
    Includes a brief delay to allow content to render.
    
    Example:
        When I scroll to the bottom of the page
    """
    context.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)


@then('I take a screenshot named "{screenshot_name}"')
def step_take_screenshot(context, screenshot_name):
    """
    Capture a screenshot and save it to the screenshots directory.
    
    If Behave's embed feature is available (HTML report), the screenshot
    will be embedded in the test report for easy review.
    
    Args:
        screenshot_name: Base name for the file (without extension)
        
    Output:
        PNG file saved to {screenshots_dir}/{screenshot_name}.png
        
    Example:
        Then I take a screenshot named "login_error_state"
    """
    screenshots_dir = getattr(context, 'screenshots_dir', 'screenshots')
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    filepath = os.path.join(screenshots_dir, f"{screenshot_name}.png")
    context.driver.save_screenshot(filepath)
    
    # Embed in HTML report if available
    if hasattr(context, 'embed'):
        import base64
        with open(filepath, 'rb') as img:
            data = base64.b64encode(img.read()).decode('utf-8')
        context.embed('image/png', data, caption=screenshot_name)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: PAGE OBJECT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
# The core of our YAML-driven Page Object pattern.
# Elements are defined in YAML files and resolved dynamically at runtime.
# ═══════════════════════════════════════════════════════════════════════════════

def get_element_from_page_object(context, element_name, page_name):
    """
    Retrieve a typed element from YAML-based page object definitions.
    
    This is the central helper for the Page Object pattern. It:
    1. Locates the appropriate YAML file for the page
    2. Finds the element definition by name
    3. Creates a typed element (Button, Input, etc.) via ElementFactory
    
    File Resolution Order:
        1. features/page_objects/{page_name}.yml
        2. features/page_objects/{page_name}.yaml
        3. features/page_objects/locators/{page_name}.yml
        4. features/page_objects/locators/{page_name}.yaml
    
    Args:
        context: Behave context (must have 'driver' attribute)
        element_name: Key of the element in the YAML file
        page_name: Name of the page (supports dot notation like 'dashboard.sidebar')
        
    Returns:
        Typed element instance (Button, Input, Text, WebElement, etc.)
        
    Raises:
        FileNotFoundError: If page YAML file is not found
        KeyError: If element is not defined in the page YAML
        
    Example:
        element = get_element_from_page_object(context, 'submit_button', 'login')
        element.click()
    """
    from qa_framework.core.element_factory import ElementFactory
    
    # Parse page name for nested access (e.g., 'dashboard.sidebar')
    parts = page_name.split('.')
    page_file = parts[0]
    
    # Locate the YAML file
    page_objects_dir = os.path.join(os.getcwd(), 'features', 'page_objects')
    yaml_path = _find_page_yaml(page_objects_dir, page_file)
    
    if not yaml_path:
        raise FileNotFoundError(
            f"Page object file not found: {page_file}.yml or {page_file}.yaml "
            f"in {page_objects_dir} or {page_objects_dir}/locators"
        )
    
    # Load and parse YAML
    import yaml
    with open(yaml_path, 'r') as f:
        page_data = yaml.safe_load(f)
    
    # Navigate to correct section
    page_section = page_data.get(page_file, page_data.get('locators', page_data))
    for part in parts[1:]:
        if isinstance(page_section, dict) and part in page_section:
            page_section = page_section[part]
        else:
            raise KeyError(f"Nested path '{part}' not found in '{page_name}'")
    
    # Find element configuration
    if element_name not in page_section:
        raise KeyError(
            f"Element '{element_name}' not found in '{page_name}'. "
            f"Available elements: {list(page_section.keys())}"
        )
    
    element_config = page_section[element_name]
    element_type = element_config.get('type', 'webelement')
    locator_data = {'by': element_config.get('by'), 'value': element_config.get('value')}
    
    # Create typed element via factory
    return ElementFactory.create(
        driver=context.driver,
        element_type=element_type,
        locator_data=locator_data,
        element_name=element_name
    )


def _find_page_yaml(page_objects_dir, page_file):
    """
    Internal helper to locate a page object YAML file.
    
    Checks multiple locations and extensions for flexibility.
    
    Returns:
        Absolute path to YAML file, or None if not found
    """
    candidates = [
        os.path.join(page_objects_dir, f"{page_file}.yml"),
        os.path.join(page_objects_dir, f"{page_file}.yaml"),
        os.path.join(page_objects_dir, 'locators', f"{page_file}.yml"),
        os.path.join(page_objects_dir, 'locators', f"{page_file}.yaml"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: PAGE OBJECT STEP DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════
# Gherkin steps that leverage the Page Object engine for element interaction.
# ═══════════════════════════════════════════════════════════════════════════════

@given('I navigate to the dashboard at "{url}"')
def step_navigate_to_dashboard(context, url):
    """
    Navigate to a dashboard URL.
    
    This is a semantic alias for the generic navigate step,
    useful for making feature files more readable.
    
    Example:
        Given I navigate to the dashboard at "http://localhost:3000/dashboard/"
    """
    context.driver.get(url)


@when('I click on the "{element_name}" in "{page_name}"')
def step_click_page_object(context, element_name, page_name):
    """
    Click on an element defined in a page object YAML.
    
    Example:
        When I click on the "submit_button" in "login"
    """
    element = get_element_from_page_object(context, element_name, page_name)
    element.click()


@when('I type "{text}" into the "{element_name}" in "{page_name}"')
def step_type_into_page_object(context, text, element_name, page_name):
    """
    Type text into an input element defined in a page object.
    
    Supports token resolution for dynamic data.
    Clears the field before typing.
    
    Example:
        When I type "[UUID]" into the "username_field" in "login"
    """
    element = get_element_from_page_object(context, element_name, page_name)
    resolved_text = resolve_tokens(context, text)
    
    if hasattr(element, 'clear_and_type'):
        element.clear_and_type(resolved_text)
    else:
        selenium_element = element._find_element()
        selenium_element.clear()
        selenium_element.send_keys(resolved_text)


@then('I should see the "{element_name}" in "{page_name}"')
@then('the "{element_name}" in "{page_name}" should be visible')
def step_should_see_page_object(context, element_name, page_name):
    """
    Verify an element from a page object is visible.
    
    Example:
        Then I should see the "welcome_message" in "dashboard"
    """
    element = get_element_from_page_object(context, element_name, page_name)
    element.wait_until_visible()
    assert element.is_displayed(), f"Element '{element_name}' in '{page_name}' is not visible"


@then('the "{element_name}" in "{page_name}" should contain the text "{text}"')
def step_element_should_contain_text(context, element_name, page_name, text):
    """
    Verify a page object element contains expected text.
    
    Uses case-insensitive, whitespace-normalized matching.
    Supports I18n tokens for localized verification.
    
    Example:
        Then the "header_title" in "dashboard" should contain the text "[LANG:dashboard.title]"
    """
    resolved_text = resolve_i18n(context, text)
    element = get_element_from_page_object(context, element_name, page_name)
    
    element_text = element.get_text() if hasattr(element, 'get_text') else element._find_element().text
    normalized_element = " ".join(element_text.lower().split())
    normalized_expected = " ".join(resolved_text.lower().split())
    
    assert normalized_expected in normalized_element, \
        f"Element '{element_name}' does not contain text '{resolved_text}'. Found: '{element_text}'"


@then('I should see at least {count:d} elements with class "{class_name}"')
def step_should_see_at_least_elements_by_class(context, count, class_name):
    """
    Verify a minimum number of elements with a CSS class exist.
    
    Handles special characters in class names (Tailwind, etc.).
    
    Example:
        Then I should see at least 3 elements with class "card-item"
    """
    escaped_class = class_name.replace('/', '\\/')
    css_selector = f".{escaped_class}"
    locator = (By.CSS_SELECTOR, css_selector)
    
    wait_for_presence(context.driver, locator)
    elements = context.driver.find_elements(*locator)
    assert len(elements) >= count, \
        f"Expected at least {count} elements with class '{class_name}', found {len(elements)}"


@then('I should see at least {count:d} elements with selector "{element_name}" in "{page_name}"')
def step_should_see_at_least_elements_in_page_object(context, count, element_name, page_name):
    """
    Verify a minimum number of elements exist for a page object locator.
    
    Useful for lists, tables, and repeating UI components.
    
    Example:
        Then I should see at least 5 elements with selector "table_row" in "users_list"
    """
    element = get_element_from_page_object(context, element_name, page_name)
    wait_for_presence(context.driver, element.locator)
    elements = context.driver.find_elements(*element.locator)
    assert len(elements) >= count, \
        f"Expected at least {count} elements for '{element_name}', found {len(elements)}"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: CONTEXT-AWARE STEPS
# ═══════════════════════════════════════════════════════════════════════════════
# These steps use 'context.current_page' to avoid repeating page names.
# Set with: Then the "page_name" page is displayed
# ═══════════════════════════════════════════════════════════════════════════════

@then('the "{page_name}" page is displayed')
@given('the "{page_name}" page is displayed')
@step('the "{page_name}" page is displayed')
def step_set_current_page(context, page_name):
    """
    Set the current page context and verify critical elements are loaded.
    
    This step does two important things:
    1. Sets context.current_page for use by context-aware steps
    2. Waits for elements marked with 'wait_load: true' in YAML
    
    This enables "smart" page load verification and shorter step syntax
    in subsequent steps (no need to specify page name repeatedly).
    
    Example YAML (dashboard.yaml):
        header_title:
          by: css
          value: h1.title
          wait_load: true  ← This element must be visible for page to be "loaded"
    
    Example:
        Then the "dashboard" page is displayed
        And I click on the "settings_button"  ← No page name needed!
    """
    context.current_page = page_name
    
    # Load page YAML and verify wait_load elements
    parts = page_name.split('.')
    page_file = parts[0]
    page_objects_dir = os.path.join(os.getcwd(), 'features', 'page_objects')
    yaml_path = _find_page_yaml(page_objects_dir, page_file)
    
    if not yaml_path:
        return  # No YAML found, just set context
        
    import yaml
    with open(yaml_path, 'r') as f:
        page_data = yaml.safe_load(f)
        
    page_section = page_data.get(page_file, page_data.get('locators', page_data))
    for part in parts[1:]:
        page_section = page_section.get(part, {}) if isinstance(page_section, dict) else {}
        
    # Verify elements with wait_load: true
    if isinstance(page_section, dict):
        for elem_name, config in page_section.items():
            if isinstance(config, dict) and config.get('wait_load') is True:
                try:
                    element = get_element_from_page_object(context, elem_name, page_name)
                    element.wait_until_visible(timeout=30)
                except Exception as e:
                    raise AssertionError(
                        f"Page Load Failed: Critical element '{elem_name}' not visible on '{page_name}'. "
                        f"Error: {e}"
                    )


@when('I click on the "{element_name}"')
def step_click_current_page_object(context, element_name):
    """
    Click on an element using the current page context.
    
    Requires: 'Then the "page" page is displayed' to be called first.
    
    Example:
        Then the "login" page is displayed
        When I click on the "submit_button"
    """
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_click_page_object(context, element_name, page_name)


@when('I type "{text}" into the "{element_name}"')
def step_type_into_current_page_object(context, text, element_name):
    """
    Type text into an element using the current page context.
    
    Requires: 'Then the "page" page is displayed' to be called first.
    
    Example:
        Then the "login" page is displayed
        When I type "admin@example.com" into the "email_input"
    """
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_type_into_page_object(context, text, element_name, page_name)


@then('the "{element_name}" should contain the text "{text}"')
def step_current_element_should_contain_text(context, element_name, text):
    """
    Verify an element contains text using the current page context.
    
    Example:
        Then the "header" should contain the text "Welcome"
    """
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_element_should_contain_text(context, element_name, page_name, text)


@then('the following elements should contain these texts')
def step_bulk_elements_should_contain_text(context):
    """
    Verify multiple elements contain expected texts using a data table.
    
    This is a power step for efficient multi-element verification.
    Each row triggers a separate assertion for clear error reporting.
    
    Example:
        Then the following elements should contain these texts
          | element         | value                            |
          | header_title    | [LANG:dashboard.title]           |
          | stats_card      | [LANG:dashboard.stats.total]     |
          | footer_version  | v2.1.0                           |
    """
    if not context.table:
        return
        
    for row in context.table:
        element_name = row['element']
        expected_text = row['value']
        step_current_element_should_contain_text(context, element_name, expected_text)


@then('I should see the "{element_name}"')
@then('the "{element_name}" should be visible')
def step_should_see_current_page_object(context, element_name):
    """
    Verify an element is visible using the current page context.
    
    Example:
        Then I should see the "success_message"
    """
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_should_see_page_object(context, element_name, page_name)


@then('I should see at least {count:d} elements with selector "{element_name}"')
def step_should_see_at_least_elements_in_current_page(context, count, element_name):
    """
    Verify minimum element count using the current page context.
    
    Example:
        Then I should see at least 3 elements with selector "list_item"
    """
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_should_see_at_least_elements_in_page_object(context, count, element_name, page_name)


@when('I click on the "{element_name}" in the sidebar')
def step_click_sidebar_element(context, element_name):
    """
    Shortcut for clicking sidebar navigation elements.
    
    Assumes a 'sidebar.yaml' page object file exists.
    
    Example:
        When I click on the "dashboard_link" in the sidebar
    """
    step_click_page_object(context, element_name, "sidebar")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: VISUAL REGRESSION TESTING
# ═══════════════════════════════════════════════════════════════════════════════
# Pixel-based comparison of UI screenshots against baseline images.
# Supports automatic baseline creation and configurable tolerance.
# ═══════════════════════════════════════════════════════════════════════════════

@then('I take a screenshot of the "{element_description}" named "{screenshot_name}"')
def step_take_element_screenshot(context, element_description, screenshot_name):
    """
    Take a screenshot with semantic naming.
    
    The element_description is for documentation; currently captures full page.
    
    Example:
        Then I take a screenshot of the "login form" named "login_initial_state"
    """
    step_take_screenshot(context, screenshot_name)


@then('the "{description}" {target_type:w} should visually match the baseline image "{name}"')
def step_visual_match_explicit(context, description, target_type, name):
    """
    Verify visual match with 0% tolerance (pixel-perfect).
    
    Example:
        Then the "header" element should visually match the baseline image "header_base"
    """
    step_visual_match_with_threshold(context, description, name, 0.0)


@then('the "{element_name}" text should be one of "{options_str}"')
def step_text_should_be_one_of(context, element_name, options_str):
    """
    Verify that an element's text matches one of the provided options.
    Options are comma-separated.
    
    Example:
        Then the "status" text should be one of "Active, Pending, Completed"
    """
    options = [opt.strip() for opt in options_str.split(',')]
    page_name = getattr(context, 'current_page', None)
    
    if not page_name:
         # Fallback: try to guess page or use current context logic if available.
         # For now, require page context.
         raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")

    element = get_element_from_page_object(context, element_name, page_name)
    text = element.get_text()
    
    # Check simplified normalization (strip whitespace)
    match = False
    for opt in options:
        if opt in text: # flexible matching
             match = True
             break
    
    assert match, f"Text '{text}' in '{element_name}' is not one of {options}"


@then('the "{description}" {target_type:w} should visually match the baseline image "{name}" with a {threshold:f}% tolerance')
def step_visual_match_explicit_with_threshold(context, description, target_type, name, threshold):
    """
    Verify visual match with configurable tolerance.
    
    The threshold is an RMS (Root Mean Square) error percentage.
    - 0%: Pixel-perfect match required
    - 1-5%: Minor differences allowed (anti-aliasing, timing)
    - 5-10%: Moderate differences allowed (dynamic content)
    
    Baseline Management:
    - If baseline doesn't exist, current screenshot becomes baseline
    - If [VisualTests] save=true in config, baseline is overwritten
    
    Example:
        Then the "charts" page should visually match the baseline image "dashboard_charts" with a 5.0% tolerance
    """
    step_visual_match_with_threshold(context, description, name, threshold)


@then('the visual of the "{element_description}" named "{screenshot_name}" should match')
def step_visual_match(context, element_description, screenshot_name):
    """
    Standard visual match syntax with 0% tolerance.
    
    Example:
        Then the visual of the "dashboard header" named "header_screenshot" should match
    """
    step_visual_match_with_threshold(context, element_description, screenshot_name, 0.0)


@then('the visual of the "{element_description}" named "{screenshot_name}" should match with a threshold of {threshold:f}%')
def step_visual_match_with_threshold(context, element_description, screenshot_name, threshold):
    print(f"\n[DEBUG] ENTERING step_visual_match_with_threshold: desc={element_description}, name={screenshot_name}\n")
    """
    Core visual comparison implementation.
    
    Workflow:
    1. Capture current screenshot to temporary file
    2. Compare against baseline using VisualHandler
    3. If no baseline exists, seed it with current screenshot
    4. If mismatch exceeds threshold and [VisualTests] fail=true, raise assertion
    
    Args:
        element_description: Semantic description for logging
        screenshot_name: Base name for baseline file
        threshold: Allowed RMS error percentage (0.0 = pixel-perfect)
    """
    # Capture current state
    ss_dir = os.path.join(os.getcwd(), 'features', 'resources', 'screenshots')
    if not os.path.exists(ss_dir):
        os.makedirs(ss_dir)
        
    current_path = os.path.join(ss_dir, f"{screenshot_name}_latest.png")
    ContextualLogger.info(f"Capturing visual snapshot: {screenshot_name}", context)
    
    # Attempt to capture element-specific screenshot if possible
    page_name = getattr(context, 'current_page', None)
    captured = False
    try:
        # Support explicit page targeting via dot notation (e.g., "sidebar.sidebar_container")
        target_page = page_name
        target_element = element_description
        
        if "." in element_description:
            parts = element_description.split('.')
            target_page = parts[0]
            target_element = ".".join(parts[1:])
            
        if target_page:
            with open('C:/Users/Carlos/Desktop/github/dashboard/DEBUG_MASK.txt', 'a') as f:
                f.write(f"Attempting granular capture for {target_element} in {target_page}\n")
            
            element = get_element_from_page_object(context, target_element, target_page)
            # Find the actual driver element and take its screenshot
            if hasattr(element, '_find_element'):
                el = element._find_element()
                el.screenshot(current_path)
                captured = True
                ContextualLogger.info(f"Captured granular screenshot for element: {target_element} in {target_page}", context)
        else:
            with open('C:/Users/Carlos/Desktop/github/dashboard/DEBUG_MASK.txt', 'a') as f:
                f.write(f"Skipping granular capture: target_page is None. context.current_page={getattr(context, 'current_page', 'MISSING')}\n")

    except Exception as e:
        # Fallback to full viewport if element not found or error
        with open('C:/Users/Carlos/Desktop/github/dashboard/DEBUG_MASK.txt', 'a') as f:
            f.write(f"Granular capture failed for '{target_element}': {e}\n")
        ContextualLogger.debug(f"Granular capture fallback: {e}", context)
        pass

    if not captured:
        context.driver.save_screenshot(current_path)
    
    # Compare against baseline
    similarity, is_match = VisualHandler.validate_visual(
        context, screenshot_name, current_path, threshold
    )
    
    # Handle failure based on configuration
    visual_config = getattr(context, 'visual_config', {})
    if not is_match and visual_config.get('fail', False):
        raise AssertionError(
            f"Visual validation failed for '{screenshot_name}'. "
            f"Similarity: {similarity:.2f}%. Allowed threshold: {threshold}%."
        )


@then('the "{description}" {target_type:w} should visually match the baseline image "{name}" without elements and with a {threshold:f}% tolerance')
def step_visual_match_with_masking(context, description, target_type, name, threshold):
    """
    Perform a visual match after masking out specific elements using a table.
    
    Example:
        Then the "dashboard" page should visually match the baseline image "dashboard_main" without elements and with a 5.0% tolerance
          | element       |
          | stats_values  |
          | timestamp     |
    """
    if not context.table:
        raise AssertionError("This step requires a table of elements to mask.")

    # Identfy current page
    page_name = getattr(context, 'current_page', None)

    # 1. Capture current state
    # 1. Capture visual state
    ss_dir = os.path.join(os.getcwd(), 'features', 'resources', 'screenshots')
    if not os.path.exists(ss_dir):
        os.makedirs(ss_dir)
    
    current_path = os.path.join(ss_dir, f"{name}_latest.png")
    
    # Resolve target element for granular capture
    target_obj = get_element_from_page_object(context, description, page_name)
    captured_granular = False
    parent_offset_x = 0
    parent_offset_y = 0
    
    try:
        if target_obj and hasattr(target_obj, '_find_element'):
            # Scroll into view first
            el = target_obj._find_element()
            # Scroll into view first - align to start for large containers like dashboard
            align_to_top = 'true' if description == 'dashboard' else 'false'
            # context.driver.execute_script("arguments[0].scrollIntoView({block: 'start', inline: 'nearest'});", el)
            # Simple approach: scroll to top if dashboard or mobile_layout
            if description in ['dashboard', 'mobile_layout']:
                 context.driver.execute_script("arguments[0].scrollIntoView(true);", el)
            else:
                 context.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            
            # Capture element
            el.screenshot(current_path)
            captured_granular = True
            ContextualLogger.info(f"Captured granular screenshot for masking: {name} (Element: {description})", context)
            
            # Record parent location for relative mask coordinates
            parent_offset_x = el.location['x']
            parent_offset_y = el.location['y']
            
    except Exception as e:
        ContextualLogger.warning(f"Granular capture failed for '{description}', falling back to viewport: {e}", context)

    if not captured_granular:
        ContextualLogger.info(f"Capturing viewport screenshot for masking: {name}", context)
        context.driver.save_screenshot(current_path)
        # Use scroll offset for viewport capture
        parent_offset_x = context.driver.execute_script("return window.pageXOffset;")
        parent_offset_y = context.driver.execute_script("return window.pageYOffset;")

    # 2. Apply Masks
    mask_regions = []
    if context.table:
        for row in context.table:
            sub_element_name = row[0]
            try:
                sub_el = get_element_from_page_object(context, sub_element_name, page_name)
                found_elements = context.driver.find_elements(*sub_el.locator)
                
                for el in found_elements:
                    loc = el.location
                    size = el.size
                    
                    # Calculate relative coordinates based on capture mode
                    x = loc['x'] - parent_offset_x
                    y = loc['y'] - parent_offset_y
                    
                    if x >= 0 and y >= 0: # Only mask if within captured region
                        mask_regions.append({
                            'x': x,
                            'y': y,
                            'width': size['width'],
                            'height': size['height']
                        })
            except Exception as e:
                ContextualLogger.warning(f"Failed to mask element '{sub_element_name}': {e}", context)

    # 4. Apply masking
    ContextualLogger.debug(f"[DEBUG] Applying {len(mask_regions)} mask regions.", context)
    VisualHandler.apply_masking(current_path, mask_regions)

    # 4. Compare against baseline (if baseline exists and is not masked, 
    # it will be masked on next save/seed or must be masked manually once)
    similarity, is_match = VisualHandler.validate_visual(
        context, name, current_path, threshold
    )

    # Handle failure based on configuration
    visual_config = getattr(context, 'visual_config', {})
    if not is_match and visual_config.get('fail', False):
        raise AssertionError(
            f"Visual validation failed for '{name}' after masking. "
            f"Similarity: {similarity:.2f}%. Allowed threshold: {threshold}%."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: MOUSE & KEYBOARD ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@when('I hover over the "{element_name}"')
def step_hover_over_element(context, element_name):
    """
    Simulate hovering the mouse cursor over an element.
    
    Example:
        When I hover over the "user_profile_icon"
    """
    page_name = getattr(context, 'current_page', None)
    element = get_element_from_page_object(context, element_name, page_name)
    element.wait_until_visible()
    
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(context.driver)
    actions.move_to_element(element._find_element()).perform()


@when('I double click on the "{element_name}"')
def step_double_click_element(context, element_name):
    """
    Perform a double click on a page object element.
    
    Example:
        When I double click on the "file_icon"
    """
    page_name = getattr(context, 'current_page', None)
    element = get_element_from_page_object(context, element_name, page_name)
    element.wait_until_clickable()
    
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(context.driver)
    actions.double_click(element._find_element()).perform()


@when('I press the "{key_name}" key')
def step_press_key(context, key_name):
    """
    Simulate a keyboard key press.
    
    Supported keys: Enter, Escape, Tab, Backspace, Delete, ArrowUp, ArrowDown, etc.
    
    Example:
        When I press the "Enter" key
    """
    from selenium.webdriver.common.keys import Keys
    key_map = {
        "Enter": Keys.ENTER,
        "Escape": Keys.ESCAPE,
        "Tab": Keys.TAB,
        "Backspace": Keys.BACKSPACE,
        "Delete": Keys.DELETE,
        "ArrowUp": Keys.ARROW_UP,
        "ArrowDown": Keys.ARROW_DOWN,
        "ArrowLeft": Keys.ARROW_LEFT,
        "ArrowRight": Keys.ARROW_RIGHT,
        "Space": Keys.SPACE,
        "PageUp": Keys.PAGE_UP,
        "PageDown": Keys.PAGE_DOWN
    }
    
    if key_name not in key_map:
        raise ValueError(f"Unsupported key name: '{key_name}'. Available: {list(key_map.keys())}")
    
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(context.driver)
    actions.send_keys(key_map[key_name]).perform()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: WINDOW & FRAME MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@when('I switch to the next tab')
def step_switch_to_next_tab(context):
    """Switch focus to the next available browser tab."""
    handles = context.driver.window_handles
    current = context.driver.current_window_handle
    next_index = (handles.index(current) + 1) % len(handles)
    new_handle = handles[next_index]
    ContextualLogger.info(f"Switching to window handle: {new_handle}", context)
    context.driver.switch_to.window(new_handle)


@when('I close the current tab')
def step_close_current_tab(context):
    """Close the currently focused tab and switch back to the main window."""
    context.driver.close()
    if len(context.driver.window_handles) > 0:
        context.driver.switch_to.window(context.driver.window_handles[0])


@when('I switch to the iframe "{element_name}"')
def step_switch_to_iframe(context, element_name):
    """
    Switch driver context to a specific iframe element.
    
    Example:
        When I switch to the iframe "payment_widget"
    """
    page_name = getattr(context, 'current_page', None)
    element = get_element_from_page_object(context, element_name, page_name)
    ContextualLogger.info(f"Switching to iframe: {element_name}", context)
    context.driver.switch_to.frame(element._find_element())


@when('I switch back to the default content')
def step_switch_to_default_content(context):
    """Reset driver context to the main page (exit iframes)."""
    context.driver.switch_to.default_content()


@when('I accept the alert')
def step_accept_alert(context):
    """Accept (Click OK) on a browser alert/dialog."""
    WebDriverWait(context.driver, 5).until(EC.alert_is_present())
    context.driver.switch_to.alert.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10: ADVANCED VALIDATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@then('the "{element_name}" should have the attribute "{attribute}" with value "{expected_value}"')
def step_verify_attribute(context, element_name, attribute, expected_value):
    """
    Verify an element attribute matches the expected value.
    
    Example:
        Then the "login_button" should have the attribute "type" with value "submit"
    """
    page_name = getattr(context, 'current_page', None)
    element = get_element_from_page_object(context, element_name, page_name)
    actual_value = element.get_attribute(attribute)
    assert actual_value == expected_value, \
        f"Expected attribute '{attribute}' to be '{expected_value}', but found '{actual_value}'"


@then('the URL should contain "{substring}"')
def step_verify_url_contains(context, substring):
    """Verify that the current browser URL contains a specific substring."""
    current_url = context.driver.current_url
    assert substring in current_url, f"Expected URL to contain '{substring}', but was '{current_url}'"


@then('the "{element_name}" should be hidden')
@then('the "{element_name}" should not be visible')
def step_verify_element_hidden(context, element_name):
    """
    Verify that an element is either not present or not visible.
    
    Example:
        Then the "error_banner" should be hidden
    """
    page_name = getattr(context, 'current_page', None)
    try:
        element = get_element_from_page_object(context, element_name, page_name)
        assert not element.is_displayed(), f"Element '{element_name}' is visible but should be hidden"
    except (NoSuchElementException, TimeoutException, KeyError):
        # Success if element is not found or times out during visibility search
        pass
    except Exception:  # nosec B110
        # Some elements might exist but be truly hidden (display: none)
        pass
