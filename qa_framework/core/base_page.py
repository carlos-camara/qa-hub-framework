from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10

    def find_element(self, locator, timeout=None):
        """Find an element with explicit wait."""
        t = timeout if timeout is not None else self.timeout
        try:
            return WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            # Re-raise with a clear message or handle globally
            raise TimeoutException(f"Element not found within {t}s: {locator}")

    def find_elements(self, locator, timeout=None):
        """Find multiple elements."""
        t = timeout if timeout is not None else self.timeout
        try:
            return WebDriverWait(self.driver, t).until(
                EC.presence_of_all_elements_located(locator)
            )
        except TimeoutException:
            return []

    def click(self, locator, timeout=None):
        """Click an element with wait."""
        t = timeout if timeout is not None else self.timeout
        element = WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()

    def send_keys(self, locator, text, timeout=None):
        """Send keys to an element."""
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)

    def is_visible(self, locator, timeout=None):
        """Check if element is visible."""
        t = timeout if timeout is not None else self.timeout
        try:
            WebDriverWait(self.driver, t).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def get_text(self, locator, timeout=None):
        """Get element text."""
        element = self.find_element(locator, timeout)
        return element.text

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
