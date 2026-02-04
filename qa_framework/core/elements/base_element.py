"""
Base WebElement class for typed page object elements.
Provides common functionality for all element types.
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Tuple, Any


class WebElement:
    """
    Base class for all typed page elements.
    Wraps Selenium WebElement with convenient methods.
    """
    
    def __init__(self, driver: Any, locator: Tuple[str, str], name: str = None):
        """
        Initialize a WebElement.
        
        Args:
            driver: Selenium WebDriver or Playwright Page wrapper
            locator: Tuple of (By type, value) e.g., (By.ID, "button-id")
            name: Optional name for better error messages
        """
        self.driver = driver
        self.locator = locator
        self.name = name or f"{locator[0]}={locator[1]}"
        self._element = None
    
    def _find_element(self, timeout: int = 10) -> Any:
        """Find and return the underlying element."""
        if hasattr(self.driver, 'page'): # PlaywrightWrapper
            return self.driver.find_element(self.locator[0], self.locator[1])
            
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.locator)
            )
        except TimeoutException:
            raise NoSuchElementException(
                f"Element '{self.name}' not found with locator {self.locator}"
            )
    
    def is_visible(self, timeout: int = 10) -> bool:
        """Check if element is visible."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_enabled(self) -> bool:
        """Check if element is enabled."""
        element = self._find_element()
        return element.is_enabled()
    
    def is_displayed(self) -> bool:
        """Check if element is displayed."""
        try:
            element = self._find_element()
            return element.is_displayed()
        except NoSuchElementException:
            return False
    
    def get_attribute(self, attribute: str) -> str:
        """Get an attribute value from the element."""
        element = self._find_element()
        return element.get_attribute(attribute)
    
    def click(self, timeout: int = 10):
        """Click the element."""
        self.wait_until_clickable(timeout)
        element = self._find_element(timeout)
        element.click()
    
    def send_keys(self, keys: str, timeout: int = 10):
        """Send keys to the element."""
        self.wait_until_visible(timeout)
        element = self._find_element(timeout)
        element.send_keys(keys)
    
    def get_text(self, timeout: int = 10) -> str:
        """Get the text content of the element."""
        self.wait_until_visible(timeout)
        element = self._find_element(timeout)
        return element.text
    
    def wait_until_visible(self, timeout: int = 10):
        """Wait until element is visible."""
        if hasattr(self.driver, 'page'):
            self.driver.page.wait_for_selector(self.driver._convert_locator(self.locator[0], self.locator[1]), state="visible", timeout=timeout*1000)
            return

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.locator)
            )
        except TimeoutException:
            raise TimeoutException(
                f"Element '{self.name}' did not become visible within {timeout} seconds"
            )
    
    def wait_until_clickable(self, timeout: int = 10):
        """Wait until element is clickable."""
        if hasattr(self.driver, 'page'):
            self.driver.page.wait_for_selector(self.driver._convert_locator(self.locator[0], self.locator[1]), state="visible", timeout=timeout*1000)
            # Playwright doesn't have a direct 'clickable' state in wait_for_selector but we can assume visible + not disabled
            return

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(self.locator)
            )
        except TimeoutException:
            raise TimeoutException(
                f"Element '{self.name}' did not become clickable within {timeout} seconds"
            )
    
    def wait_until_invisible(self, timeout: int = 10):
        """Wait until element is no longer visible."""
        if hasattr(self.driver, 'page'):
            self.driver.page.wait_for_selector(self.driver._convert_locator(self.locator[0], self.locator[1]), state="hidden", timeout=timeout*1000)
            return

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.locator)
            )
        except TimeoutException:
            raise TimeoutException(
                f"Element '{self.name}' did not become invisible within {timeout} seconds"
            )
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', locator={self.locator})"
