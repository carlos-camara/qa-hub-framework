"""
Button element type with click and text retrieval functionality.
"""
from qa_framework.core.elements.base_element import WebElement
from selenium.webdriver.common.action_chains import ActionChains


class Button(WebElement):
    """
    Represents a clickable button element.
    Provides button-specific methods like click, double_click, get_text.
    """
    
    def click(self, timeout: int = 10):
        """
        Click the button.
        
        Args:
            timeout: Maximum time to wait for element to be clickable
        """
        self.wait_until_clickable(timeout)
        element = self._find_element(timeout)
        element.click()
    
    def double_click(self, timeout: int = 10):
        """
        Double-click the button.
        
        Args:
            timeout: Maximum time to wait for element to be clickable
        """
        self.wait_until_clickable(timeout)
        element = self._find_element(timeout)
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
    
    def get_text(self) -> str:
        """Get the text content of the button."""
        element = self._find_element()
        return element.text
    
    def is_clickable(self, timeout: int = 10) -> bool:
        """Check if button is clickable."""
        try:
            self.wait_until_clickable(timeout)
            return True
        except:
            return False
    
    def hover(self, timeout: int = 10):
        """Hover over the button."""
        self.wait_until_visible(timeout)
        element = self._find_element(timeout)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
