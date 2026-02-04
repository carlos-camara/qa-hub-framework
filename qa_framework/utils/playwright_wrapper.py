"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                       Playwright Compatibility Layer                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This module provides Selenium-compatible wrappers for Playwright objects.   ║
║                                                                              ║
║  The goal is to allow existing Selenium-based test code to work with        ║
║  Playwright without modification. Simply switch web_library in config        ║
║  from 'selenium' to 'playwright' and your tests continue to work.           ║
║                                                                              ║
║  Key Classes:                                                                 ║
║  • PlaywrightWrapper: Wraps Playwright Page with WebDriver-like API         ║
║  • PlaywrightElementWrapper: Wraps ElementHandle with WebElement-like API   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


class PlaywrightWrapper:
    """
    Selenium WebDriver-compatible wrapper for Playwright Page.
    
    This class provides the same interface as Selenium's WebDriver, allowing
    existing step definitions and page objects to work without modification.
    
    Mapped Methods:
        Selenium                 → Playwright
        ─────────────────────────────────────────
        driver.get(url)          → page.goto(url)
        driver.title             → page.title()
        driver.find_element()    → page.wait_for_selector()
        driver.find_elements()   → page.query_selector_all()
        driver.save_screenshot() → page.screenshot()
        driver.execute_script()  → page.evaluate()
        driver.quit()            → browser.close() + playwright.stop()
    
    Usage:
        # Created automatically by get_driver() when web_library=playwright
        driver = get_driver()  # Returns PlaywrightWrapper
        driver.get("https://example.com")
        element = driver.find_element(By.ID, "submit")
        element.click()
    
    Attributes:
        page: Playwright Page object for direct access if needed
        browser: Playwright Browser object
        playwright: Playwright instance
        implicit_wait_time: Timeout in milliseconds (default: 5000)
    """
    
    def __init__(self, page, browser, playwright_instance):
        """
        Initialize the wrapper with Playwright objects.
        
        Args:
            page: Playwright Page instance
            browser: Playwright Browser instance
            playwright_instance: Main Playwright instance (for cleanup)
        """
        self.page = page
        self.browser = browser
        self.playwright = playwright_instance
        self.implicit_wait_time = 5000  # Default to 5 seconds
        
    def get(self, url):
        """
        Navigate to a URL.
        
        Equivalent to: driver.get(url) in Selenium
        
        Args:
            url: Full URL to navigate to
        """
        self.page.goto(url)
        
    @property
    def title(self):
        """
        Get the current page title.
        
        Returns:
            str: The page title
        """
        return self.page.title()
    
    @property
    def current_url(self):
        """
        Get the current page URL.
        
        Returns:
            str: The current URL
        """
        return self.page.url
        
    def find_element(self, by, value=None):
        """
        Find a single element using Selenium-style locators.
        
        Converts Selenium By.* locators to Playwright selectors and
        waits for the element to be present (using implicit wait timeout).
        
        Args:
            by: Selenium By type (By.ID, By.CSS_SELECTOR, etc.)
                Can also be a tuple (by, value) for compatibility
            value: Selector value (optional if by is a tuple)
            
        Returns:
            PlaywrightElementWrapper: Wrapped element with Selenium-like methods
            
        Raises:
            TimeoutError: If element is not found within implicit wait time
        """
        # Handle tuple input for compatibility
        if value is None and isinstance(by, (tuple, list)):
            by, value = by[0], by[1]
            
        selector = self._convert_locator(by, value)
        element_handle = self.page.wait_for_selector(selector, timeout=self.implicit_wait_time)
        return PlaywrightElementWrapper(element_handle, self.page, selector)
        
    def find_elements(self, by, value=None):
        """
        Find multiple elements using Selenium-style locators.
        
        Unlike find_element, this returns an empty list if no elements
        are found (does not raise an exception).
        
        Args:
            by: Selenium By type or tuple (by, value)
            value: Selector value (optional if by is a tuple)
            
        Returns:
            list[PlaywrightElementWrapper]: List of wrapped elements
        """
        if value is None and isinstance(by, (tuple, list)):
            by, value = by[0], by[1]
            
        selector = self._convert_locator(by, value)
        handles = self.page.query_selector_all(selector)
        return [PlaywrightElementWrapper(h, self.page, selector) for h in handles]
        
    def save_screenshot(self, path):
        """
        Save a screenshot of the current page.
        
        Args:
            path: File path for the screenshot (should end in .png)
        """
        self.page.screenshot(path=path)
        
    def execute_script(self, script, *args):
        """
        Execute JavaScript in the page context.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            Any: Result of the JavaScript execution
        """
        return self.page.evaluate(script, args)
        
    def quit(self):
        """
        Close the browser and stop Playwright.
        
        This should be called in the test teardown (after_scenario)
        to properly clean up resources.
        """
        self.browser.close()
        self.playwright.stop()
        
    def close(self):
        """
        Close the current page (alias for quit in single-page context).
        """
        self.quit()
        
    def maximize_window(self):
        """
        Maximize window (no-op for Playwright).
        
        Playwright uses viewport sizing instead of window sizing.
        Use set_window_size() or configure viewport in get_driver().
        """
        pass  # Playwright handles this via context viewport
        
    def set_window_size(self, width, height):
        """
        Set the browser viewport size.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        self.page.set_viewport_size({"width": int(width), "height": int(height)})
        
    def implicitly_wait(self, time_seconds):
        """
        Set the implicit wait timeout for element finding.
        
        Args:
            time_seconds: Maximum time to wait for elements (in seconds)
        """
        self.implicit_wait_time = time_seconds * 1000
        self.page.set_default_timeout(self.implicit_wait_time)

    def _convert_locator(self, by, value):
        """
        Convert Selenium By.* locator to Playwright selector format.
        
        This is the core of the compatibility layer, translating between
        Selenium's locator strategy and Playwright's selector engine.
        
        Conversion Table:
            By.ID              → #value
            By.NAME            → [name='value']
            By.XPATH           → xpath=value
            By.CSS_SELECTOR    → value (unchanged)
            By.CLASS_NAME      → .value
            By.TAG_NAME        → value
            By.LINK_TEXT       → text='value' (exact)
            By.PARTIAL_LINK_TEXT → text=value (partial)
        
        Args:
            by: Selenium By enum value
            value: Locator value string
            
        Returns:
            str: Playwright-compatible selector string
        """
        from selenium.webdriver.common.by import By
        
        if by == By.ID:
            return f"#{value}"
        elif by == By.NAME:
            return f"[name='{value}']"
        elif by == By.XPATH:
            return f"xpath={value}"
        elif by == By.CSS_SELECTOR:
            return value  # CSS selectors are the same
        elif by == By.CLASS_NAME:
            return f".{value}"
        elif by == By.TAG_NAME:
            return value
        elif by == By.LINK_TEXT:
            return f"text='{value}'"  # Exact match
        elif by == By.PARTIAL_LINK_TEXT:
            return f"text={value}"  # Partial match
        return value


class PlaywrightElementWrapper:
    """
    Selenium WebElement-compatible wrapper for Playwright ElementHandle.
    
    Provides the same interface as Selenium's WebElement, allowing existing
    test code to interact with elements without modification.
    
    Mapped Methods:
        Selenium                 → Playwright
        ─────────────────────────────────────────
        element.click()          → handle.click()
        element.send_keys(text)  → handle.type(text)
        element.clear()          → handle.fill("")
        element.text             → handle.inner_text()
        element.get_attribute()  → handle.get_attribute()
        element.is_displayed()   → handle.is_visible()
        element.is_enabled()     → handle.is_enabled()
        element.is_selected()    → handle.is_checked()
    
    Attributes:
        handle: Playwright ElementHandle for direct access
        page: Parent Playwright Page
        selector: The selector used to find this element
    """
    
    def __init__(self, handle, page, selector):
        """
        Initialize the element wrapper.
        
        Args:
            handle: Playwright ElementHandle
            page: Parent Playwright Page
            selector: Selector string used to find this element
        """
        self.handle = handle
        self.page = page
        self.selector = selector
        
    def click(self):
        """
        Click the element.
        
        Playwright automatically waits for the element to be actionable
        (visible, stable, not obscured, enabled) before clicking.
        """
        self.handle.click()
        
    def send_keys(self, keys):
        """
        Type text into the element or press special keys.
        
        Handles both regular text input and Selenium special keys
        (Keys.ENTER, Keys.TAB, etc.).
        
        Args:
            keys: String to type or Selenium Keys constant
        """
        from selenium.webdriver.common.keys import Keys
        
        # Map Selenium special keys to Playwright key names
        key_map = {
            Keys.ENTER: "Enter",
            Keys.RETURN: "Enter",
            Keys.TAB: "Tab",
            Keys.ESCAPE: "Escape",
            Keys.BACKSPACE: "Backspace",
            Keys.DELETE: "Delete",
            Keys.ARROW_UP: "ArrowUp",
            Keys.ARROW_DOWN: "ArrowDown",
            Keys.ARROW_LEFT: "ArrowLeft",
            Keys.ARROW_RIGHT: "ArrowRight",
        }
        
        if keys in key_map:
            self.handle.press(key_map[keys])
        else:
            # Use type() to simulate keystroke-by-keystroke typing
            # This preserves existing content (like Selenium's send_keys)
            self.handle.type(str(keys))
        
    def clear(self):
        """
        Clear the element's content.
        
        For input fields, this removes all text.
        """
        self.handle.fill("")
        
    @property
    def text(self):
        """
        Get the visible text content of the element.
        
        Returns:
            str: The inner text (visible text only, no HTML)
        """
        return self.handle.inner_text()
    
    def get_text(self):
        """
        Get the visible text content (method version for compatibility).
        
        Returns:
            str: The inner text
        """
        return self.text
        
    def get_attribute(self, name):
        """
        Get an attribute value from the element.
        
        Args:
            name: Attribute name (e.g., 'href', 'class', 'data-id')
            
        Returns:
            str: Attribute value, or None if not present
        """
        return self.handle.get_attribute(name)
        
    def is_displayed(self):
        """
        Check if the element is visible.
        
        Returns:
            bool: True if visible, False otherwise
        """
        return self.handle.is_visible()
        
    def is_enabled(self):
        """
        Check if the element is enabled (not disabled).
        
        Returns:
            bool: True if enabled, False if disabled
        """
        return self.handle.is_enabled()
    
    def is_selected(self):
        """
        Check if the element is selected (for checkboxes/radios).
        
        Returns:
            bool: True if checked/selected, False otherwise
        """
        return self.handle.is_checked()
        
    def screenshot(self, path):
        """
        Take a screenshot of just this element.
        
        Args:
            path: File path for the screenshot
        """
        self.handle.screenshot(path=path)
    
    def find_element(self, by, value=None):
        """
        Find a child element within this element.
        
        Args:
            by: Selenium By type or tuple
            value: Selector value
            
        Returns:
            PlaywrightElementWrapper: Wrapped child element
        """
        if value is None and isinstance(by, (tuple, list)):
            by, value = by[0], by[1]
        
        # Create relative selector
        from selenium.webdriver.common.by import By
        if by == By.XPATH:
            # For XPath, we need to use a Page-level query with the combined selector
            full_selector = f"{self.selector} >> xpath={value}"
            handle = self.page.wait_for_selector(full_selector, timeout=5000)
        else:
            # For CSS, we can use query_selector on the handle
            wrapper = PlaywrightWrapper(self.page, None, None)
            selector = wrapper._convert_locator(by, value)
            handle = self.handle.query_selector(selector)
        
        return PlaywrightElementWrapper(handle, self.page, value)
