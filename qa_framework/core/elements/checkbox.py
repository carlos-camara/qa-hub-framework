"""
Checkbox element type for checkbox inputs.
Provides semantic methods for checking, unchecking, and state verification.
"""
from qa_framework.core.elements.base_element import WebElement


class Checkbox(WebElement):
    """
    Represents a checkbox input element.
    
    Provides checkbox-specific methods like check, uncheck, toggle,
    and state verification (is_checked).
    
    Example usage:
        checkbox = Checkbox(driver, (By.ID, "terms-checkbox"), "Terms Agreement")
        checkbox.check()
        assert checkbox.is_checked()
    """
    
    def is_checked(self, timeout: int = 10) -> bool:
        """
        Check if the checkbox is currently checked.
        
        Returns:
            True if checked, False otherwise
        """
        element = self._find_element(timeout)
        return element.is_selected()
    
    def check(self, timeout: int = 10):
        """
        Check the checkbox if not already checked.
        
        Args:
            timeout: Maximum time to wait for element to be clickable
        """
        if not self.is_checked(timeout):
            self.click(timeout)
    
    def uncheck(self, timeout: int = 10):
        """
        Uncheck the checkbox if currently checked.
        
        Args:
            timeout: Maximum time to wait for element to be clickable
        """
        if self.is_checked(timeout):
            self.click(timeout)
    
    def toggle(self, timeout: int = 10):
        """
        Toggle the checkbox state.
        
        Args:
            timeout: Maximum time to wait for element to be clickable
        """
        self.click(timeout)
    
    def set_state(self, checked: bool, timeout: int = 10):
        """
        Set the checkbox to a specific state.
        
        Args:
            checked: True to check, False to uncheck
            timeout: Maximum time to wait for element
        """
        if checked:
            self.check(timeout)
        else:
            self.uncheck(timeout)
    
    def get_label(self, timeout: int = 10) -> str:
        """
        Get the associated label text for the checkbox.
        
        This attempts to find the label via the 'for' attribute or parent element.
        
        Returns:
            Label text if found, empty string otherwise
        """
        element = self._find_element(timeout)
        
        # Try to get label via 'for' attribute
        checkbox_id = element.get_attribute('id')
        if checkbox_id:
            try:
                from selenium.webdriver.common.by import By
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                return label.text
            except Exception:
                pass
        
        # Try parent label
        try:
            parent = element.find_element(By.XPATH, "./ancestor::label")
            return parent.text
        except Exception:
            pass
        
        return ""
