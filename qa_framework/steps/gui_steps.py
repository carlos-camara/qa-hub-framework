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
