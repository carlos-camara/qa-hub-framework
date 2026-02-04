"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                          Element Factory                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This module provides the ElementFactory class, which creates typed           ║
║  element instances from YAML page object definitions.                        ║
║                                                                              ║
║  The factory pattern enables:                                                 ║
║  • Automatic element type detection from YAML 'type' field                   ║
║  • Locator strategy parsing (CSS, XPath, ID, etc.)                           ║
║  • Custom element type registration for project-specific elements            ║
║  • Clean separation between YAML configuration and element behavior          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from typing import Tuple, Dict, Type, Any

# Import all element types
from qa_framework.core.elements.base_element import WebElement
from qa_framework.core.elements.button import Button
from qa_framework.core.elements.buttons import Buttons
from qa_framework.core.elements.input import Input
from qa_framework.core.elements.text import Text
from qa_framework.core.elements.texts import Texts
from qa_framework.core.elements.checkbox import Checkbox
from qa_framework.core.elements.radio import RadioButton
from qa_framework.core.elements.link import Link
from qa_framework.core.elements.select import Select


class ElementFactory:
    """
    Factory for creating typed page object elements from YAML definitions.
    
    This class bridges the gap between YAML-based locator definitions and
    strongly-typed Python element classes. When a step definition requests
    an element by name, the factory:
    
    1. Reads the 'type' field from the YAML definition
    2. Maps it to the appropriate element class (Button, Input, etc.)
    3. Parses the locator strategy ('by') and value
    4. Creates and returns a typed element instance
    
    Element Type Mapping:
        YAML type        Python class       Use case
        ─────────────────────────────────────────────────────────────
        button          Button              Click-able buttons
        buttons         Buttons             Collections of buttons
        input           Input               Text input fields
        checkbox        Checkbox            Checkable elements
        radio           RadioButton         Radio button options
        link            Link                Anchor (<a>) elements
        select          Select              Dropdown selects
        text            Text                Read-only text elements
        texts           Texts               Collections of text
        webelement      WebElement          Generic fallback
    
    Locator Strategy Mapping:
        YAML 'by'       Selenium By         Example
        ─────────────────────────────────────────────────────────────
        id              By.ID               #submit-btn
        name            By.NAME             [name='email']
        xpath           By.XPATH            //button[@type='submit']
        css             By.CSS_SELECTOR     .btn-primary
        class           By.CLASS_NAME       btn-primary
        tag             By.TAG_NAME         button
        link_text       By.LINK_TEXT        <a>Exact Text</a>
        partial_link_text By.PARTIAL_LINK   <a>Partial...</a>
    
    Example YAML (features/page_objects/locators/login.yaml):
        submit_button:
          type: button
          by: id
          value: submit-btn
          
        email_input:
          type: input
          by: css
          value: input[name='email']
    
    Usage in Steps:
        element = ElementFactory.create(
            driver=context.driver,
            element_type='button',
            locator_data={'by': 'id', 'value': 'submit-btn'},
            element_name='submit_button'
        )
        element.click()
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # TYPE MAPPINGS
    # ─────────────────────────────────────────────────────────────────────────
    
    ELEMENT_TYPE_MAP: Dict[str, Type[WebElement]] = {
        # Interactive elements
        'button': Button,
        'buttons': Buttons,
        'input': Input,
        'checkbox': Checkbox,
        'radio': RadioButton,
        'link': Link,
        'select': Select,
        # Read-only elements
        'text': Text,
        'texts': Texts,
        # Generic fallback
        'webelement': WebElement,
    }
    """
    Mapping of YAML 'type' strings to Python element classes.
    
    Use register_custom_element() to add project-specific element types.
    """
    
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
    """
    Mapping of YAML 'by' strings to Selenium By constants.
    
    These are the supported locator strategies for finding elements.
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # FACTORY METHOD
    # ─────────────────────────────────────────────────────────────────────────
    
    @classmethod
    def create(
        cls,
        driver: Any,
        element_type: str,
        locator_data: Dict,
        element_name: str = None
    ) -> WebElement:
        """
        Create a typed element instance from configuration data.
        
        This is the main factory method called by get_element_from_page_object()
        in gui_steps.py. It takes the parsed YAML data and returns a fully
        functional, typed element ready for interaction.
        
        Args:
            driver: WebDriver instance (Selenium or PlaywrightWrapper)
            element_type: Type identifier from YAML (e.g., 'button', 'input')
            locator_data: Dictionary with 'by' and 'value' keys
            element_name: Optional friendly name for error messages
            
        Returns:
            Typed element instance (Button, Input, Select, etc.)
            Returns WebElement if type is unknown (with warning)
            
        Raises:
            ValueError: If element_type or locator 'by' type is unknown
            
        Example:
            # From YAML config:
            # submit_button:
            #   type: button
            #   by: id
            #   value: submit-btn
            
            element = ElementFactory.create(
                driver=driver,
                element_type='button',
                locator_data={'by': 'id', 'value': 'submit-btn'},
                element_name='submit_button'
            )
            
            # element is now a Button instance with click(), is_enabled(), etc.
        """
        # ─────────────────────────────────────────────────────────────────────
        # Step 1: Resolve element class from type string
        # ─────────────────────────────────────────────────────────────────────
        element_class = cls.ELEMENT_TYPE_MAP.get(element_type.lower())
        if element_class is None:
            raise ValueError(
                f"Unknown element type '{element_type}'. "
                f"Available types: {list(cls.ELEMENT_TYPE_MAP.keys())}"
            )
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 2: Parse locator strategy and value
        # ─────────────────────────────────────────────────────────────────────
        by_type_str = locator_data.get('by', '').lower()
        by_value = locator_data.get('value', '')
        
        by_type = cls.BY_TYPE_MAP.get(by_type_str)
        if by_type is None:
            raise ValueError(
                f"Unknown locator type '{by_type_str}'. "
                f"Available types: {list(cls.BY_TYPE_MAP.keys())}"
            )
        
        locator: Tuple[str, str] = (by_type, by_value)
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 3: Instantiate and return the typed element
        # ─────────────────────────────────────────────────────────────────────
        return element_class(driver, locator, element_name)
    
    # ─────────────────────────────────────────────────────────────────────────
    # EXTENSIBILITY
    # ─────────────────────────────────────────────────────────────────────────
    
    @classmethod
    def register_custom_element(cls, type_name: str, element_class: Type[WebElement]):
        """
        Register a custom element type for project-specific elements.
        
        Use this to extend the factory with custom element classes that
        have specialized behavior for your application's unique UI components.
        
        Args:
            type_name: String identifier to use in YAML 'type' field
            element_class: Element class to instantiate (must extend WebElement)
            
        Example:
            # In your project's environment.py or steps file:
            
            class DatePicker(WebElement):
                def set_date(self, date_string):
                    # Custom date picker logic
                    pass
                    
            ElementFactory.register_custom_element('datepicker', DatePicker)
            
            # Now in YAML:
            # birth_date:
            #   type: datepicker
            #   by: id
            #   value: birth-date-picker
        """
        cls.ELEMENT_TYPE_MAP[type_name.lower()] = element_class
    
    @classmethod
    def get_available_types(cls) -> list:
        """
        Get a list of all registered element types.
        
        Returns:
            list: Sorted list of available type strings
        """
        return sorted(cls.ELEMENT_TYPE_MAP.keys())
