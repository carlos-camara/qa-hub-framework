"""
Texts collection element type for multiple text elements.
"""
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple
from qa_framework.core.elements.text import Text


class Texts:
    """
    Represents a collection of text elements.
    Useful for working with multiple text elements at once.
    """
    
    def __init__(self, driver: WebDriver, locator: Tuple[str, str], name: str = None):
        """
        Initialize a Texts collection.
        
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
        """Get the number of text elements in the collection."""
        elements = self._find_elements()
        return len(elements)
    
    def get_all_texts(self) -> List[str]:
        """Get text from all elements in the collection."""
        elements = self._find_elements()
        return [element.text for element in elements]
    
    def contains_text(self, text: str) -> bool:
        """
        Check if any element in the collection contains the specified text.
        
        Args:
            text: Text to search for
            
        Returns:
            True if any element contains the text, False otherwise
        """
        all_texts = self.get_all_texts()
        return any(text in t for t in all_texts)
    
    def get_by_index(self, index: int) -> Text:
        """
        Get a Text instance for a specific index.
        
        Args:
            index: Zero-based index of the text element
            
        Returns:
            Text instance for the specified index
        """
        elements = self._find_elements()
        if index < 0 or index >= len(elements):
            raise IndexError(f"Text index {index} out of range (0-{len(elements)-1})")
        
        # Create a locator for this specific text element
        from selenium.webdriver.common.by import By
        specific_locator = (By.XPATH, f"({self.locator[1]})[{index + 1}]")
        return Text(self.driver, specific_locator, f"{self.name}[{index}]")
    
    def find_by_text(self, text: str) -> Text:
        """
        Find and return the first Text element that contains the specified text.
        
        Args:
            text: Text to search for
            
        Returns:
            Text instance for the first matching element
        """
        elements = self._find_elements()
        for i, element in enumerate(elements):
            if text in element.text:
                from selenium.webdriver.common.by import By
                specific_locator = (By.XPATH, f"({self.locator[1]})[{i + 1}]")
                return Text(self.driver, specific_locator, f"{self.name}[{i}]")
        
        raise ValueError(f"No text element found containing '{text}'")
