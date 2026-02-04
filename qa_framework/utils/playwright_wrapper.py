"""
Selenium-compatible wrapper for Playwright Page object.
"""

class PlaywrightWrapper:
    def __init__(self, page, browser, playwright_instance):
        self.page = page
        self.browser = browser
        self.playwright = playwright_instance
        self.implicit_wait_time = 5000 # Default to 5s
        
    def get(self, url):
        self.page.goto(url)
        
    @property
    def title(self):
        return self.page.title()
        
    def find_element(self, by, value=None):
        if value is None and isinstance(by, (tuple, list)):
            by, value = by[0], by[1]
        selector = self._convert_locator(by, value)
        # Playwright's locator doesn't wait by default until accessed, 
        # but we want to mimic Selenium's behavior of throwing if not found
        element_handle = self.page.wait_for_selector(selector, timeout=self.implicit_wait_time)
        return PlaywrightElementWrapper(element_handle, self.page, selector)
        
    def find_elements(self, by, value=None):
        if value is None and isinstance(by, (tuple, list)):
            by, value = by[0], by[1]
        selector = self._convert_locator(by, value)
        handles = self.page.query_selector_all(selector)
        return [PlaywrightElementWrapper(h, self.page, selector) for h in handles]
        
    def save_screenshot(self, path):
        self.page.screenshot(path=path)
        
    def execute_script(self, script, *args):
        return self.page.evaluate(script, args)
        
    def quit(self):
        self.browser.close()
        self.playwright.stop()
        
    def maximize_window(self):
        # Playwright handles this via context viewport
        pass
        
    def set_window_size(self, width, height):
        self.page.set_viewport_size({"width": int(width), "height": int(height)})
        
    def implicitly_wait(self, time_seconds):
        self.implicit_wait_time = time_seconds * 1000
        self.page.set_default_timeout(self.implicit_wait_time)

    def _convert_locator(self, by, value):
        """Converts Selenium 'By' to Playwright selector."""
        from selenium.webdriver.common.by import By
        if by == By.ID:
            return f"#{value}"
        elif by == By.NAME:
            return f"[name='{value}']"
        elif by == By.XPATH:
            return f"xpath={value}"
        elif by == By.CSS_SELECTOR:
            return value
        elif by == By.CLASS_NAME:
            return f".{value}"
        elif by == By.TAG_NAME:
            return value
        elif by == By.LINK_TEXT:
            return f"text='{value}'"
        elif by == By.PARTIAL_LINK_TEXT:
            return f"text={value}"
        return value

class PlaywrightElementWrapper:
    def __init__(self, handle, page, selector):
        self.handle = handle
        self.page = page
        self.selector = selector
        
    def click(self):
        self.handle.click()
        
    def send_keys(self, keys):
        # Handle Selenium special keys (like ENTER, TAB)
        from selenium.webdriver.common.keys import Keys
        key_map = {
            Keys.ENTER: "Enter",
            Keys.RETURN: "Enter",
            Keys.TAB: "Tab",
            Keys.ESCAPE: "Escape",
            Keys.BACKSPACE: "Backspace",
            Keys.DELETE: "Delete"
        }
        
        if keys in key_map:
            self.handle.press(key_map[keys])
        else:
            # Selenium's send_keys appends. Playwright's fill replaces.
            # We use press_sequentially (modern 'type') to mimic appending if focused,
            # or just fill if starting from clear.
            self.handle.type(str(keys))
        
    def clear(self):
        self.handle.fill("")
        
    @property
    def text(self):
        return self.handle.inner_text()
        
    def get_attribute(self, name):
        return self.handle.get_attribute(name)
        
    def is_displayed(self):
        return self.handle.is_visible()
        
    def is_enabled(self):
        return self.handle.is_enabled()
        
    def screenshot(self, path):
        self.handle.screenshot(path=path)
