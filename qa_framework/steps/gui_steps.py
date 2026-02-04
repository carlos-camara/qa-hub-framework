from behave import given, when, then, step
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from ..core.language_handler import LanguageHandler
from ..utils.visual import VisualHandler

def wait_for_visible(driver, locator, timeout=10):
    """Agnostic wait for visibility."""
    if hasattr(driver, 'page'):
        selector = driver._convert_locator(locator[0], locator[1])
        driver.page.wait_for_selector(selector, state="visible", timeout=timeout*1000)
    else:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))

def wait_for_clickable(driver, locator, timeout=10):
    """Agnostic wait for clickability."""
    if hasattr(driver, 'page'):
        selector = driver._convert_locator(locator[0], locator[1])
        driver.page.wait_for_selector(selector, state="visible", timeout=timeout*1000)
    else:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))

def wait_for_presence(driver, locator, timeout=10):
    """Agnostic wait for presence."""
    if hasattr(driver, 'page'):
        selector = driver._convert_locator(locator[0], locator[1])
        driver.page.wait_for_selector(selector, state="attached", timeout=timeout*1000)
    else:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def wait_for_title(driver, title, timeout=10):
    """Agnostic wait for title."""
    if hasattr(driver, 'page'):
        # Playwright doesn't have a direct title wait, so we poll
        import time
        start = time.time()
        while time.time() - start < timeout:
            if driver.title == title:
                return True
            time.sleep(0.5)
        raise TimeoutException(f"Title '{title}' not found. Current: '{driver.title}'")
    else:
        WebDriverWait(driver, timeout).until(EC.title_is(title))

from selenium.common.exceptions import TimeoutException

def resolve_tokens(context, text):
    """
    Resolve tokens in the text.
    Order: Variables ([UUID], [NOW], etc) -> I18n ([LANG:key])
    """
    if not isinstance(text, str):
        return text
        
    resolved = text
    
    # 1. Resolve Variables
    if hasattr(context, 'variables'):
        resolved = context.variables.resolve(resolved)
    
    # 2. Resolve I18n (if it's still a string and has the tag)
    if isinstance(resolved, str) and hasattr(context, 'i18n'):
        resolved = context.i18n.resolve(resolved)
        
    return resolved

def resolve_i18n(context, text):
    """Legacy wrapper for resolve_tokens"""
    return resolve_tokens(context, text)

@given('I navigate to "{url}"')
def step_navigate_to_url(context, url):
    context.driver.get(url)

@then('the page title should be "{expected_title}"')
def step_verify_page_title(context, expected_title):
    resolved_title = resolve_i18n(context, expected_title)
    wait_for_title(context.driver, resolved_title)
    assert context.driver.title == resolved_title

@when('I click on the element with text "{text}"')
def step_click_element_by_text(context, text):
    resolved_text = resolve_i18n(context, text)
    # Using a generic XPath for text matching
    locator = (By.XPATH, f"//*[contains(text(), '{resolved_text}')]")
    wait_for_clickable(context.driver, locator)
    element = context.driver.find_element(*locator)
    element.click()

@when('I click on the button with text "{button_text}"')
def step_click_button_by_text(context, button_text):
    resolved_text = resolve_i18n(context, button_text)
    # Use XPath with translate for case-insensitive matching
    xpath = f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{resolved_text.lower()}')]"
    locator = (By.XPATH, xpath)
    wait_for_clickable(context.driver, locator)
    element = context.driver.find_element(*locator)
    element.click()

@then('I should see the text "{text}"')
def step_verify_text_present(context, text):
    # Resolve i18n if applicable
    resolved_text = resolve_i18n(context, text)
    
    # Check body text for case-insensitive match with normalized whitespace
    body_text = context.driver.find_element(By.TAG_NAME, "body").text
    normalized_body = " ".join(body_text.lower().split())
    normalized_expected = " ".join(resolved_text.lower().split())
    assert normalized_expected in normalized_body, f"Text '{resolved_text}' not found (case-insensitive normalized search in body). Found sample: '{normalized_body[:100]}...'"

@then('I should see an element with class "{class_name}"')
def step_verify_element_by_class(context, class_name):
    locator = (By.CLASS_NAME, class_name)
    wait_for_visible(context.driver, locator)
    element = context.driver.find_element(*locator)
    assert element.is_displayed()

@when('I scroll to the bottom of the page')
def step_scroll_to_bottom(context):
    context.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)

@then('I take a screenshot named "{screenshot_name}"')
def step_take_screenshot(context, screenshot_name):
    screenshots_dir = getattr(context, 'screenshots_dir', 'screenshots')
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    filepath = os.path.join(screenshots_dir, f"{screenshot_name}.png")
    context.driver.save_screenshot(filepath)
    if hasattr(context, 'embed'):
        import base64
        with open(filepath, 'rb') as img:
            data = base64.b64encode(img.read()).decode('utf-8')
        context.embed('image/png', data, caption=screenshot_name)

# ==================== Page Object-based Steps ====================

def get_element_from_page_object(context, element_name, page_name):
    """
    Helper to retrieve a typed element from YAML page objects.
    Supports nested notation like "dashboard.recent_runs".
    
    Returns a typed element instance (Button, Input, Text, etc.) based on the 'type' field.
    """
    from qa_framework.core.element_factory import ElementFactory
    
    # Split page name by dots for nested access
    parts = page_name.split('.')
    page_file = parts[0]
    
    # Load the page object YAML from the current working directory
    page_objects_dir = os.path.join(os.getcwd(), 'features', 'page_objects')
    
    # Try both .yml and .yaml extensions
    yaml_path = os.path.join(page_objects_dir, f"{page_file}.yml")
    if not os.path.exists(yaml_path):
        yaml_path = os.path.join(page_objects_dir, f"{page_file}.yaml")
    
    # Also check in locators subdirectory
    if not os.path.exists(yaml_path):
        locators_dir = os.path.join(page_objects_dir, 'locators')
        yaml_path = os.path.join(locators_dir, f"{page_file}.yml")
        if not os.path.exists(yaml_path):
            yaml_path = os.path.join(locators_dir, f"{page_file}.yaml")
    
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Page object file not found: {page_file}.yml or {page_file}.yaml in {page_objects_dir} or {page_objects_dir}/locators")
    
    import yaml
    with open(yaml_path, 'r') as f:
        page_data = yaml.safe_load(f)
    
    # Navigate to the correct page section
    if page_file in page_data:
        page_section = page_data[page_file]
    else:
        page_section = page_data.get('locators', page_data)
    
    # Handle additional nesting like "dashboard.recent_runs"
    for part in parts[1:]:
        if isinstance(page_section, dict) and part in page_section:
            page_section = page_section[part]
        else:
            raise KeyError(f"Nested path '{part}' not found in '{page_name}'")
    
    # Find the element by name
    if element_name not in page_section:
        raise KeyError(
            f"Element '{element_name}' not found in '{page_name}'. "
            f"Available elements: {list(page_section.keys())}"
        )
    
    element_config = page_section[element_name]
    
    # Get the type from the element config, default to 'webelement' if not specified
    element_type = element_config.get('type', 'webelement')
    
    # Create locator data dict (by and value)
    locator_data = {
        'by': element_config.get('by'),
        'value': element_config.get('value')
    }
    
    # Create and return typed element using ElementFactory
    element = ElementFactory.create(
        driver=context.driver,
        element_type=element_type,
        locator_data=locator_data,
        element_name=element_name
    )
    
    return element

@given('I navigate to the dashboard at "{url}"')
def step_navigate_to_dashboard(context, url):
    context.driver.get(url)

@when('I click on the "{element_name}" in "{page_name}"')
def step_click_page_object(context, element_name, page_name):
    element = get_element_from_page_object(context, element_name, page_name)
    element.click()

@when('I type "{text}" into the "{element_name}" in "{page_name}"')
def step_type_into_page_object(context, text, element_name, page_name):
    element = get_element_from_page_object(context, element_name, page_name)
    
    # Resolve tokens (I18n and Variables)
    resolved_text = resolve_tokens(context, text)
    
    # Check if element is an Input, otherwise fall back to Selenium send_keys
    if hasattr(element, 'clear_and_type'):
        element.clear_and_type(resolved_text)
    else:
        # Fallback for non-Input elements
        selenium_element = element._find_element()
        selenium_element.clear()
        selenium_element.send_keys(resolved_text)

@then('I should see the "{element_name}" in "{page_name}"')
@then('the "{element_name}" in "{page_name}" should be visible')
def step_should_see_page_object(context, element_name, page_name):
    element = get_element_from_page_object(context, element_name, page_name)
    element.wait_until_visible()
    assert element.is_displayed(), f"Element '{element_name}' in '{page_name}' is not visible"

@then('the "{element_name}" in "{page_name}" should contain the text "{text}"')
def step_element_should_contain_text(context, element_name, page_name, text):
    """Verify that a specific element contains expected text"""
    # Resolve i18n if applicable
    resolved_text = resolve_i18n(context, text)
    
    element = get_element_from_page_object(context, element_name, page_name)
    
    # Get text using appropriate method based on element type
    if hasattr(element, 'get_text'):
        element_text = element.get_text()
    else:
        element_text = element._find_element().text
    
    # Normalize whitespace for multi-line comparison (e.g., <br /> tags)
    normalized_element = " ".join(element_text.lower().split())
    normalized_expected = " ".join(resolved_text.lower().split())
    
    assert normalized_expected in normalized_element, \
        f"Element '{element_name}' in '{page_name}' does not contain text '{resolved_text}' (case-insensitive normalized). Found: '{element_text}'"

@then('I should see at least {count:d} elements with class "{class_name}"')
def step_should_see_at_least_elements_by_class(context, count, class_name):
    # Use CSS selector to handle Tailwind classes with special characters like "bg-slate-950/40"
    # Escape special characters for CSS selector
    escaped_class = class_name.replace('/', '\\/')
    css_selector = f".{escaped_class}"
    locator = (By.CSS_SELECTOR, css_selector)
    
    wait_for_presence(context.driver, locator)
    elements = context.driver.find_elements(*locator)
    assert len(elements) >= count, f"Expected at least {count} elements with class '{class_name}', found {len(elements)}"

@then('I should see at least {count:d} elements with selector "{element_name}" in "{page_name}"')
def step_should_see_at_least_elements_in_page_object(context, count, element_name, page_name):
    """Verify a minimum number of elements exist for a given page object locator"""
    element = get_element_from_page_object(context, element_name, page_name)
    
    # We use the underlying locator from the typed element
    wait_for_presence(context.driver, element.locator)
    elements = context.driver.find_elements(*element.locator)
    assert len(elements) >= count, \
        f"Expected at least {count} elements for '{element_name}' in '{page_name}', found {len(elements)}"

@then('the "{page_name}" page is displayed')
@given('the "{page_name}" page is displayed')
@step('the "{page_name}" page is displayed')
def step_set_current_page(context, page_name):
    """
    Set the current page context for subsequent steps and verify critical elements load.
    Checks for 'wait_load: true' in the page object YAML.
    """
    context.current_page = page_name
    
    # Logic to find and verify elements with wait_load: true
    # We reuse parts of get_element_from_page_object logic here
    parts = page_name.split('.')
    page_file = parts[0]
    
    page_objects_dir = os.path.join(os.getcwd(), 'features', 'page_objects')
    yaml_path = os.path.join(page_objects_dir, f"{page_file}.yml")
    if not os.path.exists(yaml_path):
        yaml_path = os.path.join(page_objects_dir, f"{page_file}.yaml")
    if not os.path.exists(yaml_path):
        locators_dir = os.path.join(page_objects_dir, 'locators')
        yaml_path = os.path.join(locators_dir, f"{page_file}.yml")
        if not os.path.exists(yaml_path):
            yaml_path = os.path.join(locators_dir, f"{page_file}.yaml")
            
    if not os.path.exists(yaml_path):
        return # Fallback: if YAML not found, just set context and proceed
        
    import yaml
    with open(yaml_path, 'r') as f:
        page_data = yaml.safe_load(f)
        
    if page_file in page_data:
        page_section = page_data[page_file]
    else:
        page_section = page_data.get('locators', page_data)
        
    for part in parts[1:]:
        if isinstance(page_section, dict) and part in page_section:
            page_section = page_section[part]
        else:
            page_section = {} # Path not found
            break
            
    # Verify elements with wait_load: true
    if isinstance(page_section, dict):
        for element_name, config in page_section.items():
            if isinstance(config, dict) and config.get('wait_load') is True:
                try:
                    element = get_element_from_page_object(context, element_name, page_name)
                    element.wait_until_visible(timeout=10)
                except Exception as e:
                    raise AssertionError(
                        f"Page Load Failed: Critical element '{element_name}' with wait_load: true "
                        f"was not found or not visible on '{page_name}' page. Error: {str(e)}"
                    )

@when('I click on the "{element_name}"')
def step_click_current_page_object(context, element_name):
    """Context-aware click: uses context.current_page if available"""
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_click_page_object(context, element_name, page_name)

@when('I type "{text}" into the "{element_name}"')
def step_type_into_current_page_object(context, text, element_name):
    """Context-aware type: uses context.current_page if available"""
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_type_into_page_object(context, text, element_name, page_name)

@then('the "{element_name}" should contain the text "{text}"')
def step_current_element_should_contain_text(context, element_name, text):
    """Context-aware text containment: uses context.current_page if available"""
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_element_should_contain_text(context, element_name, page_name, text)

@then('the following elements should contain these texts')
def step_bulk_elements_should_contain_text(context):
    """
    Verify multiple elements contain expected texts using a table.
    Example:
      Then the following elements should contain these texts:
        | element           | value                                     |
        | stats_passed_card | [LANG:dashboard.stats.system_health]    |
    """
    if not context.table:
        return
        
    for row in context.table:
        element_name = row['element']
        expected_text = row['value']
        # Call the existing verification logic for each row
        step_current_element_should_contain_text(context, element_name, expected_text)

@then('I should see the "{element_name}"')
@then('the "{element_name}" should be visible')
def step_should_see_current_page_object(context, element_name):
    """Context-aware visibility: uses context.current_page if available"""
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_should_see_page_object(context, element_name, page_name)

@then('I should see at least {count:d} elements with selector "{element_name}"')
def step_should_see_at_least_elements_in_current_page(context, count, element_name):
    """Context-aware count: uses context.current_page if available"""
    page_name = getattr(context, 'current_page', None)
    if not page_name:
        raise AttributeError("No current page set. Use 'Then the \"page\" page is displayed' first.")
    step_should_see_at_least_elements_in_page_object(context, count, element_name, page_name)

@when('I click on the "{element_name}" in the sidebar')
def step_click_sidebar_element(context, element_name):
    """Shortcut for clicking sidebar elements"""
    step_click_page_object(context, element_name, "sidebar")

@then('I take a screenshot of the "{element_description}" named "{screenshot_name}"')
def step_take_element_screenshot(context, element_description, screenshot_name):
    """
    Take a screenshot. 
    Currently a proxy for full page screenshot, but standardized in the framework.
    """
    step_take_screenshot(context, screenshot_name)

@then('the "{description}" {target_type:w} should visually match the baseline image "{name}"')
def step_visual_match_explicit(context, description, target_type, name):
    """
    Explicit visual/image match with 0% threshold.
    Example: Then the "header" element should visually match the baseline image "header_base"
    """
    step_visual_match_with_threshold(context, description, name, 0.0)

@then('the "{description}" {target_type:w} should visually match the baseline image "{name}" with a {threshold:f}% tolerance')
def step_visual_match_explicit_with_threshold(context, description, target_type, name, threshold):
    """
    Explicit visual/image comparison with a percentage tolerance.
    Example: Then the "charts" page should visually match the baseline image "dashboard_charts" with a 5.0% tolerance
    """
    step_visual_match_with_threshold(context, description, name, threshold)

@then('the visual of the "{element_description}" named "{screenshot_name}" should match')
def step_visual_match(context, element_description, screenshot_name):
    """
    Standard visual match with 0% threshold.
    """
    step_visual_match_with_threshold(context, element_description, screenshot_name, 0.0)

@then('the visual of the "{element_description}" named "{screenshot_name}" should match with a threshold of {threshold:f}%')
def step_visual_match_with_threshold(context, element_description, screenshot_name, threshold):
    """
    Visual comparison with a percentage threshold for differences.
    """
    # 1. Take a temporary screenshot for comparison
    ss_dir = os.path.join(os.getcwd(), 'features', 'resources', 'screenshots')
    if not os.path.exists(ss_dir):
        os.makedirs(ss_dir)
        
    current_path = os.path.join(ss_dir, f"{screenshot_name}_latest.png")
    context.driver.save_screenshot(current_path)
    
    # 2. Validate against baseline
    similarity, is_match = VisualHandler.validate_visual(context, screenshot_name, current_path, threshold)
    
    # 3. Handle failure
    visual_config = getattr(context, 'visual_config', {})
    should_fail = visual_config.get('fail', False)
    
    if not is_match and should_fail:
        raise AssertionError(
            f"Visual validation failed for '{screenshot_name}'. "
            f"Similarity: {similarity:.2f}%. Allowed error threshold: {threshold}%."
        )
