"""
Buttons collection element type for multiple buttons.
"""
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple
from qa_framework.core.elements.button import Button


class Buttons:
    """
    Represents a collection of button elements.
    Useful for working with multiple buttons at once.
    """
    
    def __init__(self, driver: WebDriver, locator: Tuple[str, str], name: str = None):
        """
        Initialize a Buttons collection.
        
        Args:
            driver: Selenium WebDriver instance
            locator: Tuple of (By type, value) to find multiple elements
            name: Optional name for better error messages
        """
        self.driver = driver
        self.locator = locator
        self.name = name or f"{locator[0]}={locator[1]}"
    
    def _find_elements(self) -> List:
        """Find all matching elements."""
        return self.driver.find_elements(*self.locator)
    
    def count(self) -> int:
        """Get the number of buttons in the collection."""
        elements = self._find_elements()
        return len(elements)
    
    def click_by_index(self, index: int):
        """
        Click a button by its index in the collection.
        
        Args:
            index: Zero-based index of the button to click
        """
        elements = self._find_elements()
        if index < 0 or index >= len(elements):
            raise IndexError(f"Button index {index} out of range (0-{len(elements)-1})")
        elements[index].click()
    
    def click_by_text(self, text: str):
        """
        Click the first button that contains the specified text.
        
        Args:
            text: Text to search for in button text
        """
        elements = self._find_elements()
        for element in elements:
            if text in element.text:
                element.click()
                return
        raise ValueError(f"No button found with text containing '{text}'")
    
    def get_all_texts(self) -> List[str]:
        """Get text from all buttons in the collection."""
        elements = self._find_elements()
        return [element.text for element in elements]
    
    def get_by_index(self, index: int) -> Button:
        """
        Get a Button instance for a specific index.
        
        Args:
            index: Zero-based index of the button
            
        Returns:
            Button instance for the specified index
        """
        elements = self._find_elements()
        if index < 0 or index >= len(elements):
            raise IndexError(f"Button index {index} out of range (0-{len(elements)-1})")
        
        # Create a locator for this specific button
        # Note: This is a simplified approach, might need refinement
        from selenium.webdriver.common.by import By
        specific_locator = (By.XPATH, f"({self.locator[1]})[{index + 1}]")
        return Button(self.driver, specific_locator, f"{self.name}[{index}]")
