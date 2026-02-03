from behave import step, when, then
from selenium.webdriver.common.by import By
import time
import os

@step('I wait for {seconds:d} seconds')
def step_wait_seconds(context, seconds):
    """Explicit wait."""
    time.sleep(seconds)

@then('I take a screenshot named "{screenshot_name}"')
def step_take_screenshot(context, screenshot_name):
    """Takes a screenshot."""
    if not hasattr(context, 'driver'):
        return

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

@then('I should see the text "{text}"')
def step_verify_text_present(context, text):
    """Generic text verification."""
    # This requires context to have a current page or driver access
    # Ideally, framework steps should rely on a standard context structure
    # For now, we assume simple driver check or page object if set
    assert text in context.driver.page_source, f"Text '{text}' not found."

@then('the page URL should contain "{url_fragment}"')
def step_verify_url_contains(context, url_fragment):
    assert url_fragment in context.driver.current_url, f"URL mismatch: {context.driver.current_url}"
