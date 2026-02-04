"""
RadioButton element type for radio input groups.
Provides semantic methods for selection and state verification.
"""
from qa_framework.core.elements.base_element import WebElement
from typing import List, Tuple, Any


class RadioButton(WebElement):
    """
    Represents a single radio button element.
    
    Provides radio-specific methods like select and is_selected.
    
    Example usage:
        gender_male = RadioButton(driver, (By.ID, "gender-male"), "Male Option")
        gender_male.select()
        assert gender_male.is_selected()
    """
    
    def is_selected(self, timeout: int = 10) -> bool:
        """
        Check if this radio button is currently selected.
        
        Returns:
            True if selected, False otherwise
        """
        element = self._find_element(timeout)
        return element.is_selected()
    
    def select(self, timeout: int = 10):
        """
        Select this radio button.
        
        Args:
            timeout: Maximum time to wait for element to be clickable
        """
        if not self.is_selected(timeout):
            self.click(timeout)
    
    def get_value(self, timeout: int = 10) -> str:
        """
        Get the value attribute of the radio button.
        
        Returns:
            The value attribute
        """
        return self.get_attribute('value')
    
    def get_label(self, timeout: int = 10) -> str:
        """
        Get the associated label text for the radio button.
        
        Returns:
            Label text if found, empty string otherwise
        """
        element = self._find_element(timeout)
        
        # Try to get label via 'for' attribute
        radio_id = element.get_attribute('id')
        if radio_id:
            try:
                from selenium.webdriver.common.by import By
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                return label.text
            except Exception:  # nosec B110 - Intentional fallback
                pass
        
        # Try parent label
        try:
            from selenium.webdriver.common.by import By
            parent = element.find_element(By.XPATH, "./ancestor::label")
            return parent.text
        except Exception:  # nosec B110 - Intentional fallback
            pass
        
        return ""


class RadioGroup:
    """
    Represents a group of radio buttons with the same name.
    
    Provides methods to select by value, get selected option, and list all options.
    
    Example usage:
        payment_method = RadioGroup(driver, "payment_method")
        payment_method.select_by_value("credit_card")
        assert payment_method.get_selected_value() == "credit_card"
    """
    
    def __init__(self, driver: Any, name: str, group_name: str = None):
        """
        Initialize a RadioGroup.
        
        Args:
            driver: Selenium WebDriver or Playwright wrapper
            name: The 'name' attribute shared by all radio buttons in the group
            group_name: Optional friendly name for error messages
        """
        self.driver = driver
        self.name = name
        self.group_name = group_name or f"RadioGroup[name='{name}']"
    
    def _get_all_radios(self) -> List:
        """Get all radio buttons in this group."""
        from selenium.webdriver.common.by import By
        return self.driver.find_elements(By.CSS_SELECTOR, f"input[type='radio'][name='{self.name}']")
    
    def get_options(self) -> List[str]:
        """
        Get all available option values in the group.
        
        Returns:
            List of value attributes
        """
        radios = self._get_all_radios()
        return [r.get_attribute('value') for r in radios]
    
    def get_selected_value(self) -> str:
        """
        Get the currently selected value.
        
        Returns:
            Value of the selected radio, or None if none selected
        """
        radios = self._get_all_radios()
        for radio in radios:
            if radio.is_selected():
                return radio.get_attribute('value')
        return None
    
    def select_by_value(self, value: str, timeout: int = 10):
        """
        Select a radio button by its value.
        
        Args:
            value: The value attribute to match
            timeout: Maximum time to wait
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        locator = (By.CSS_SELECTOR, f"input[type='radio'][name='{self.name}'][value='{value}']")
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
        element = self.driver.find_element(*locator)
        element.click()
    
    def select_by_index(self, index: int, timeout: int = 10):
        """
        Select a radio button by its index in the group.
        
        Args:
            index: Zero-based index
            timeout: Maximum time to wait
        """
        radios = self._get_all_radios()
        if index < 0 or index >= len(radios):
            raise IndexError(f"Index {index} out of range for {self.group_name} (has {len(radios)} options)")
        radios[index].click()
    
    def __repr__(self):
        return f"RadioGroup(name='{self.name}', options={self.get_options()})"
