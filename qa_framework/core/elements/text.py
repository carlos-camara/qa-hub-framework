"""
Text element type for read-only text elements.
"""
from qa_framework.core.elements.base_element import WebElement
import re


class Text(WebElement):
    """
    Represents a text element (headings, paragraphs, labels, etc.).
    Provides text-specific methods like get_text, contains, matches_regex.
    """
    
    def get_text(self) -> str:
        """Get the text content of the element."""
        element = self._find_element()
        return element.text
    
    def contains(self, substring: str) -> bool:
        """
        Check if text contains a substring.
        
        Args:
            substring: Substring to search for
            
        Returns:
            True if substring is found, False otherwise
        """
        text = self.get_text()
        return substring in text
    
    def matches_regex(self, pattern: str) -> bool:
        """
        Check if text matches a regular expression pattern.
        
        Args:
            pattern: Regular expression pattern
            
        Returns:
            True if pattern matches, False otherwise
        """
        text = self.get_text()
        return bool(re.match(pattern, text))
    
    def get_inner_html(self) -> str:
        """Get the inner HTML of the element."""
        return self.get_attribute('innerHTML')
    
    def is_empty(self) -> bool:
        """Check if the text element is empty."""
        text = self.get_text()
        return len(text.strip()) == 0
