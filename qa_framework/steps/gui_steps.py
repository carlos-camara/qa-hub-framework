from behave import given, when, then, step
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

@given('I navigate to "{url}"')
def step_navigate_to_url(context, url):
    context.driver.get(url)

@then('the page title should be "{expected_title}"')
def step_verify_page_title(context, expected_title):
    WebDriverWait(context.driver, 10).until(EC.title_is(expected_title))
    assert context.driver.title == expected_title

@when('I click on the element with text "{text}"')
def step_click_element_by_text(context, text):
    # Using a generic XPath for text matching
    locator = (By.XPATH, f"//*[contains(text(), '{text}')]")
    element = WebDriverWait(context.driver, 10).until(EC.element_to_be_clickable(locator))
    element.click()

@when('I click on the button with text "{button_text}"')
def step_click_button_by_text(context, button_text):
    locator = (By.XPATH, f"//button[contains(text(), '{button_text}')]")
    element = WebDriverWait(context.driver, 10).until(EC.element_to_be_clickable(locator))
    element.click()

@then('I should see the text "{text}"')
def step_verify_text_present(context, text):
    assert text in context.driver.page_source, f"Text '{text}' not found."

@then('I should see an element with class "{class_name}"')
def step_verify_element_by_class(context, class_name):
    locator = (By.CLASS_NAME, class_name)
    element = WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located(locator))
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
    
    Returns a typed element instance (Button, Input, Text, etc.) instead of a raw locator.
    """
    from qa_framework.core.element_factory import ElementFactory
    
    # Split page name by dots for nested access
    parts = page_name.split('.')
    page_file = parts[0]
    
    # Load the page object YAML from the current working directory
    # This assumes Behave is run from the project root where features/ exists
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
    
    # Navigate nested structure if needed
    # First, check if the page name itself is a root key in the YAML
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
    
    # Search for the element in type-based sections
    element_types = ['buttons', 'inputs', 'texts', 'webelements']
    found_type = None
    locator_data = None
    
    for element_type in element_types:
        if element_type in page_section:
            if element_name in page_section[element_type]:
                found_type = element_type.rstrip('s')  # buttons -> button, texts -> text
                locator_data = page_section[element_type][element_name]
                break
    
    # Fallback: check if element is directly in page_section (old format support)
    if locator_data is None and element_name in page_section:
        locator_data = page_section[element_name]
        found_type = 'webelement'  # Default to generic element
    
    if locator_data is None:
        raise KeyError(
            f"Element '{element_name}' not found in '{page_name}'. "
            f"Checked sections: {element_types}. "
            f"Available elements: {list(page_section.keys())}"
        )
    
    # Create and return typed element using ElementFactory
    element = ElementFactory.create(
        driver=context.driver,
        element_type=found_type,
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
    # Check if element is an Input, otherwise fall back to Selenium send_keys
    if hasattr(element, 'clear_and_type'):
        element.clear_and_type(text)
    else:
        # Fallback for non-Input elements
        selenium_element = element._find_element()
        selenium_element.clear()
        selenium_element.send_keys(text)

@then('I should see the "{element_name}" in "{page_name}"')
def step_should_see_page_object(context, element_name, page_name):
    element = get_element_from_page_object(context, element_name, page_name)
    element.wait_until_visible()
    assert element.is_displayed(), f"Element '{element_name}' in '{page_name}' is not visible"

@then('I should see at least {count:d} elements with class "{class_name}"')
def step_should_see_at_least_elements_by_class(context, count, class_name):
    # Use CSS selector to handle Tailwind classes with special characters like "bg-slate-950/40"
    # Escape special characters for CSS selector
    escaped_class = class_name.replace('/', '\\/')
    css_selector = f".{escaped_class}"
    
    elements = WebDriverWait(context.driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
    )
    assert len(elements) >= count, f"Expected at least {count} elements with class '{class_name}', found {len(elements)}"
