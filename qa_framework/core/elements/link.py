"""
Link element type for anchor elements.
Provides semantic methods for navigation and link inspection.
"""
from qa_framework.core.elements.base_element import WebElement


class Link(WebElement):
    """
    Represents an anchor (<a>) element.
    
    Provides link-specific methods like get_href, get_target,
    and navigation utilities.
    
    Example usage:
        home_link = Link(driver, (By.CSS_SELECTOR, "a.nav-home"), "Home Navigation")
        print(home_link.get_href())
        home_link.click()
    """
    
    def get_href(self, timeout: int = 10) -> str:
        """
        Get the href attribute (destination URL) of the link.
        
        Returns:
            The href value, or empty string if not present
        """
        return self.get_attribute('href') or ""
    
    def get_target(self, timeout: int = 10) -> str:
        """
        Get the target attribute of the link.
        
        Returns:
            The target value (e.g., '_blank', '_self'), or empty string if not present
        """
        return self.get_attribute('target') or ""
    
    def opens_in_new_tab(self, timeout: int = 10) -> bool:
        """
        Check if the link opens in a new tab.
        
        Returns:
            True if target is '_blank', False otherwise
        """
        return self.get_target(timeout) == "_blank"
    
    def get_link_text(self, timeout: int = 10) -> str:
        """
        Get the visible text of the link.
        
        Returns:
            The anchor text
        """
        return self.get_text(timeout)
    
    def is_external(self, timeout: int = 10) -> bool:
        """
        Check if the link points to an external domain.
        
        Compares the link's href domain against the current page domain.
        
        Returns:
            True if external, False if internal or same-page
        """
        from urllib.parse import urlparse
        
        href = self.get_href(timeout)
        if not href or href.startswith('#') or href.startswith('javascript:'):
            return False
        
        try:
            link_domain = urlparse(href).netloc
            current_domain = urlparse(self.driver.current_url).netloc
            return link_domain != current_domain and link_domain != ""
        except Exception:
            return False
    
    def is_broken(self, timeout: int = 10) -> bool:
        """
        Check if the link is potentially broken (no href or empty href).
        
        Note: This does NOT make an HTTP request to verify the link works.
        
        Returns:
            True if href is missing or empty
        """
        href = self.get_href(timeout)
        return not href or href == "#" or href.startswith("javascript:void")
    
    def get_download_filename(self, timeout: int = 10) -> str:
        """
        Get the download attribute value if this is a download link.
        
        Returns:
            Download filename if specified, empty string otherwise
        """
        return self.get_attribute('download') or ""
    
    def is_download_link(self, timeout: int = 10) -> bool:
        """
        Check if this link triggers a download.
        
        Returns:
            True if download attribute is present
        """
        element = self._find_element(timeout)
        return element.get_attribute('download') is not None
    
    def has_rel_noopener(self, timeout: int = 10) -> bool:
        """
        Check if the link has rel='noopener' for security.
        
        Returns:
            True if noopener is in the rel attribute
        """
        rel = self.get_attribute('rel') or ""
        return 'noopener' in rel.lower()
