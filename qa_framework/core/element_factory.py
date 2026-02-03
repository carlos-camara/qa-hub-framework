"""
ElementFactory for creating typed page element instances.
Maps element type strings to element classes.
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from typing import Tuple, Dict, Type

from qa_framework.core.elements.base_element import WebElement
from qa_framework.core.elements.button import Button
from qa_framework.core.elements.buttons import Buttons
from qa_framework.core.elements.input import Input
from qa_framework.core.elements.text import Text
from qa_framework.core.elements.texts import Texts


class ElementFactory:
    """
    Factory class to create typed element instances based on element type.
    """
    
    # Mapping of element type strings to element classes
    ELEMENT_TYPE_MAP: Dict[str, Type[WebElement]] = {
        'button': Button,
        'buttons': Buttons,
        'input': Input,
        'text': Text,
        'texts': Texts,
        'webelement': WebElement,  # Generic fallback
    }
    
    # Mapping of locator strategy strings to Selenium By constants
    BY_TYPE_MAP: Dict[str, str] = {
        'id': By.ID,
        'name': By.NAME,
        'xpath': By.XPATH,
        'css': By.CSS_SELECTOR,
        'class': By.CLASS_NAME,
        'tag': By.TAG_NAME,
        'link_text': By.LINK_TEXT,
        'partial_link_text': By.PARTIAL_LINK_TEXT,
    }
    
    @classmethod
    def create(
        cls,
        driver: WebDriver,
        element_type: str,
        locator_data: Dict,
        element_name: str = None
    ) -> WebElement:
        """
        Create a typed element instance.
        
        Args:
            driver: Selenium WebDriver instance
            element_type: Type of element ('button', 'input', 'text', etc.)
            locator_data: Dictionary containing 'by' and 'value' keys
            element_name: Optional name for the element
            
        Returns:
            Typed element instance (Button, Input, Text, etc.)
            
        Raises:
            ValueError: If element_type or locator 'by' type is unknown
        """
        # Get the element class for this type
        element_class = cls.ELEMENT_TYPE_MAP.get(element_type.lower())
        if element_class is None:
            raise ValueError(
                f"Unknown element type '{element_type}'. "
                f"Available types: {list(cls.ELEMENT_TYPE_MAP.keys())}"
            )
        
        # Parse the locator
        by_type_str = locator_data.get('by', '').lower()
        by_value = locator_data.get('value', '')
        
        by_type = cls.BY_TYPE_MAP.get(by_type_str)
        if by_type is None:
            raise ValueError(
                f"Unknown locator type '{by_type_str}'. "
                f"Available types: {list(cls.BY_TYPE_MAP.keys())}"
            )
        
        locator: Tuple[str, str] = (by_type, by_value)
        
        # Create and return the element instance
        return element_class(driver, locator, element_name)
    
    @classmethod
    def register_custom_element(cls, type_name: str, element_class: Type[WebElement]):
        """
        Register a custom element type.
        
        Args:
            type_name: String identifier for the element type
            element_class: Element class to instantiate for this type
        """
        cls.ELEMENT_TYPE_MAP[type_name.lower()] = element_class
