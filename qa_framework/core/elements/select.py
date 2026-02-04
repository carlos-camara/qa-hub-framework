"""
Select element type for dropdown/select elements.
Provides semantic methods for option selection and inspection.
"""
from qa_framework.core.elements.base_element import WebElement
from selenium.webdriver.support.ui import Select as SeleniumSelect
from typing import List


class Select(WebElement):
    """
    Represents a <select> dropdown element.
    
    Wraps Selenium's Select class with additional convenience methods
    and consistent error handling.
    
    Example usage:
        country_dropdown = Select(driver, (By.ID, "country"), "Country Selector")
        country_dropdown.select_by_visible_text("United States")
        print(country_dropdown.get_selected_text())
    """
    
    def _get_select(self, timeout: int = 10) -> SeleniumSelect:
        """Get Selenium Select wrapper for the element."""
        element = self._find_element(timeout)
        return SeleniumSelect(element)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Selection Methods
    # ─────────────────────────────────────────────────────────────────────────
    
    def select_by_visible_text(self, text: str, timeout: int = 10):
        """
        Select an option by its visible text.
        
        Args:
            text: The visible text of the option to select
            timeout: Maximum time to wait for element
        """
        self.wait_until_visible(timeout)
        select = self._get_select(timeout)
        select.select_by_visible_text(text)
    
    def select_by_value(self, value: str, timeout: int = 10):
        """
        Select an option by its value attribute.
        
        Args:
            value: The value attribute of the option to select
            timeout: Maximum time to wait for element
        """
        self.wait_until_visible(timeout)
        select = self._get_select(timeout)
        select.select_by_value(value)
    
    def select_by_index(self, index: int, timeout: int = 10):
        """
        Select an option by its index (0-based).
        
        Args:
            index: The zero-based index of the option to select
            timeout: Maximum time to wait for element
        """
        self.wait_until_visible(timeout)
        select = self._get_select(timeout)
        select.select_by_index(index)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Deselection Methods (for multi-select)
    # ─────────────────────────────────────────────────────────────────────────
    
    def deselect_all(self, timeout: int = 10):
        """
        Deselect all options (only works for multi-select).
        
        Raises:
            NotImplementedError: If the select is not multi-select
        """
        select = self._get_select(timeout)
        select.deselect_all()
    
    def deselect_by_visible_text(self, text: str, timeout: int = 10):
        """
        Deselect an option by its visible text (only works for multi-select).
        
        Args:
            text: The visible text of the option to deselect
        """
        select = self._get_select(timeout)
        select.deselect_by_visible_text(text)
    
    def deselect_by_value(self, value: str, timeout: int = 10):
        """
        Deselect an option by its value attribute (only works for multi-select).
        
        Args:
            value: The value attribute of the option to deselect
        """
        select = self._get_select(timeout)
        select.deselect_by_value(value)
    
    def deselect_by_index(self, index: int, timeout: int = 10):
        """
        Deselect an option by its index (only works for multi-select).
        
        Args:
            index: The zero-based index of the option to deselect
        """
        select = self._get_select(timeout)
        select.deselect_by_index(index)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Getters
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_selected_text(self, timeout: int = 10) -> str:
        """
        Get the visible text of the currently selected option.
        
        Returns:
            The text of the first selected option
        """
        select = self._get_select(timeout)
        return select.first_selected_option.text
    
    def get_selected_value(self, timeout: int = 10) -> str:
        """
        Get the value attribute of the currently selected option.
        
        Returns:
            The value of the first selected option
        """
        select = self._get_select(timeout)
        return select.first_selected_option.get_attribute('value')
    
    def get_all_selected_texts(self, timeout: int = 10) -> List[str]:
        """
        Get visible texts of all selected options (for multi-select).
        
        Returns:
            List of selected option texts
        """
        select = self._get_select(timeout)
        return [opt.text for opt in select.all_selected_options]
    
    def get_all_selected_values(self, timeout: int = 10) -> List[str]:
        """
        Get values of all selected options (for multi-select).
        
        Returns:
            List of selected option values
        """
        select = self._get_select(timeout)
        return [opt.get_attribute('value') for opt in select.all_selected_options]
    
    def get_all_options_text(self, timeout: int = 10) -> List[str]:
        """
        Get visible texts of all available options.
        
        Returns:
            List of all option texts
        """
        select = self._get_select(timeout)
        return [opt.text for opt in select.options]
    
    def get_all_options_values(self, timeout: int = 10) -> List[str]:
        """
        Get values of all available options.
        
        Returns:
            List of all option values
        """
        select = self._get_select(timeout)
        return [opt.get_attribute('value') for opt in select.options]
    
    def get_options_count(self, timeout: int = 10) -> int:
        """
        Get the number of available options.
        
        Returns:
            Count of options in the select
        """
        select = self._get_select(timeout)
        return len(select.options)
    
    # ─────────────────────────────────────────────────────────────────────────
    # State Checks
    # ─────────────────────────────────────────────────────────────────────────
    
    def is_multiple(self, timeout: int = 10) -> bool:
        """
        Check if this is a multi-select dropdown.
        
        Returns:
            True if multiple selections are allowed
        """
        element = self._find_element(timeout)
        return element.get_attribute('multiple') is not None
    
    def has_option_with_text(self, text: str, timeout: int = 10) -> bool:
        """
        Check if an option with specific text exists.
        
        Args:
            text: The text to search for
            
        Returns:
            True if an option with this text exists
        """
        return text in self.get_all_options_text(timeout)
    
    def has_option_with_value(self, value: str, timeout: int = 10) -> bool:
        """
        Check if an option with specific value exists.
        
        Args:
            value: The value to search for
            
        Returns:
            True if an option with this value exists
        """
        return value in self.get_all_options_values(timeout)
    
    # Override get_text to return selected text
    def get_text(self, timeout: int = 10) -> str:
        """
        Get the text of the currently selected option.
        
        This override makes Select compatible with generic text verification steps.
        
        Returns:
            Selected option text
        """
        return self.get_selected_text(timeout)
