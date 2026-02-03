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

def get_locator_from_page_object(context, locator_name, page_name):
    """
    Helper to retrieve locator from YAML page objects.
    Supports nested notation like "dashboard.recent_runs".
    """
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
    locators = page_data.get('locators', {})
    for part in parts[1:]:
        locators = locators.get(part, {})
    
    if locator_name not in locators:
        raise KeyError(f"Locator '{locator_name}' not found in '{page_name}'")
    
    locator_data = locators[locator_name]
    by_type = locator_data['by']
    value = locator_data['value']
    
    # Convert string 'by' to Selenium By constant
    by_mapping = {
        'id': By.ID,
        'name': By.NAME,
        'xpath': By.XPATH,
        'css': By.CSS_SELECTOR,
        'class': By.CLASS_NAME,
        'tag': By.TAG_NAME,
        'link_text': By.LINK_TEXT,
        'partial_link_text': By.PARTIAL_LINK_TEXT
    }
    return (by_mapping[by_type], value)

@given('I navigate to the dashboard at "{url}"')
def step_navigate_to_dashboard(context, url):
    context.driver.get(url)

@when('I click on the "{locator_name}" in "{page_name}"')
def step_click_page_object(context, locator_name, page_name):
    locator = get_locator_from_page_object(context, locator_name, page_name)
    element = WebDriverWait(context.driver, 10).until(EC.element_to_be_clickable(locator))
    element.click()

@when('I type "{text}" into the "{locator_name}" in "{page_name}"')
def step_type_into_page_object(context, text, locator_name, page_name):
    locator = get_locator_from_page_object(context, locator_name, page_name)
    element = WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located(locator))
    element.clear()
    element.send_keys(text)

@then('I should see the "{locator_name}" in "{page_name}"')
def step_should_see_page_object(context, locator_name, page_name):
    locator = get_locator_from_page_object(context, locator_name, page_name)
    element = WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located(locator))
    assert element.is_displayed()

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
