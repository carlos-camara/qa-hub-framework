"""
Input element type for text input fields.
"""
from qa_framework.core.elements.base_element import WebElement
from selenium.webdriver.common.keys import Keys


class Input(WebElement):
    """
    Represents a text input field element.
    Provides input-specific methods like type, clear, get_value.
    """
    
    def type(self, text: str, timeout: int = 10):
        """
        Type text into the input field.
        
        Args:
            text: Text to type
            timeout: Maximum time to wait for element to be visible
        """
        self.wait_until_visible(timeout)
        element = self._find_element(timeout)
        element.send_keys(text)
    
    def clear(self, timeout: int = 10):
        """Clear the input field."""
        self.wait_until_visible(timeout)
        element = self._find_element(timeout)
        element.clear()
    
    def clear_and_type(self, text: str, timeout: int = 10):
        """
        Clear the input field and type new text.
        
        Args:
            text: Text to type after clearing
            timeout: Maximum time to wait for element
        """
        self.clear(timeout)
        self.type(text, timeout)
    
    def get_value(self) -> str:
        """Get the current value of the input field."""
        return self.get_attribute('value')
    
    def get_text(self) -> str:
        """Alias for get_value to support generic text verification steps."""
        return self.get_value()
    
    def append(self, text: str, timeout: int = 10):
        """
        Append text to existing value without clearing.
        
        Args:
            text: Text to append
            timeout: Maximum time to wait for element
        """
        self.type(text, timeout)
    
    def press_enter(self, timeout: int = 10):
        """Press Enter key in the input field."""
        self.wait_until_visible(timeout)
        element = self._find_element(timeout)
        element.send_keys(Keys.RETURN)
    
    def press_tab(self, timeout: int = 10):
        """Press Tab key in the input field."""
        self.wait_until_visible(timeout)
        element = self._find_element(timeout)
        element.send_keys(Keys.TAB)
