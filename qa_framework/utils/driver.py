"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                         WebDriver Factory                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This module provides a unified driver factory for creating browser          ║
║  instances. It supports both Selenium WebDriver and Playwright, with         ║
║  automatic driver management and configuration via properties.cfg.           ║
║                                                                              ║
║  Supported Browsers:                                                          ║
║  • Chrome (Selenium + Playwright)                                            ║
║  • Firefox (Selenium + Playwright)                                           ║
║  • Edge (Selenium + Playwright)                                              ║
║  • WebKit/Safari (Playwright only)                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os
import re
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from .driver_manager import DriverManager

# Playwright is optional - gracefully handle if not installed
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_config_variable(config, value):
    """
    Resolve configuration variable references in a string.
    
    Enables dynamic configuration where one setting can reference another.
    Useful for constructing URLs or paths that depend on other config values.
    
    Pattern Format:
        {Section_Option} → Replaced with config[Section][Option]
    
    Args:
        config: ConfigParser instance with loaded configuration
        value: String potentially containing {Section_Option} patterns
        
    Returns:
        String with all patterns replaced by their config values.
        Unmatched patterns are left unchanged.
        
    Example:
        # In properties.cfg:
        # [Server]
        # host = localhost
        # port = 3000
        # [Test]
        # base_url = http://{Server_host}:{Server_port}
        
        resolve_config_variable(config, "http://{Server_host}:{Server_port}")
        → "http://localhost:3000"
    """
    if not isinstance(value, str):
        return value
        
    pattern = r'\{(\w+)_(\w+)\}'
    
    def replacer(match):
        section = match.group(1)
        option = match.group(2)
        if config.has_section(section) and config.has_option(section, option):
            return config.get(section, option)
        return match.group(0)  # Return original if not found
        
    return re.sub(pattern, replacer, value)


def get_config():
    """
    Load configuration from the project's properties.cfg file.
    
    Looks for config at: {cwd}/features/config/properties.cfg
    
    The configuration file uses INI format with sections:
    
    [Driver]
    type = chrome          # Browser: chrome, firefox, edge, webkit
    web_library = selenium # Library: selenium or playwright
    headless = true        # Run without visible browser window
    window_width = 1920    # Custom window dimensions
    window_height = 1080
    
    [Server]
    host = localhost
    port = 3000
    
    Returns:
        ConfigParser: Loaded configuration (empty if file doesn't exist)
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), 'features', 'config', 'properties.cfg')
    if os.path.exists(config_path):
        config.read(config_path)
    return config


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DRIVER FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def get_driver(headless=True, no_sandbox=True, window_size="1365,768"):
    """
    Create and return a configured browser driver instance.
    
    This is the main entry point for obtaining a browser driver. It:
    1. Reads configuration from properties.cfg
    2. Determines which library to use (Selenium or Playwright)
    3. Selects the appropriate browser
    4. Configures driver options (headless, window size, etc.)
    5. Automatically downloads the driver binary if needed
    
    Configuration Priority:
        1. properties.cfg [Driver] section (highest priority)
        2. Function arguments (fallback)
        3. Hardcoded defaults (lowest priority)
    
    Args:
        headless: Run browser without visible window (default: True)
                  Can be overridden by [Driver] headless in config
        no_sandbox: Disable Chrome sandbox for CI environments (default: True)
                    Required for Docker/Linux without proper permissions
        window_size: Window dimensions as "width,height" (default: "1365,768")
                     Overridden by window_width/window_height in config
    
    Returns:
        WebDriver: Selenium WebDriver instance, or
        PlaywrightWrapper: Playwright Page wrapped with Selenium-compatible API
        
    Configuration Example (features/config/properties.cfg):
        [Driver]
        type = chrome
        web_library = playwright
        headless = true
        window_width = 1920
        window_height = 1080
    
    Usage:
        # In environment.py
        def before_scenario(context, scenario):
            context.driver = get_driver()
        
        def after_scenario(context, scenario):
            context.driver.quit()
    """
    config = get_config()
    driver_type = "chrome"
    width = None
    height = None
    web_library = "selenium"
    
    # --- Read configuration if available ---
    if config.has_section('Driver'):
        driver_type = config.get('Driver', 'type', fallback='chrome').lower()
        web_library = config.get('Driver', 'web_library', fallback='selenium').lower()
        if config.has_option('Driver', 'headless'):
            headless = config.getboolean('Driver', 'headless')
        width = config.get('Driver', 'window_width', fallback=None)
        height = config.get('Driver', 'window_height', fallback=None)

    # --- Playwright path ---
    if web_library == "playwright":
        return get_playwright_driver(driver_type, headless, width, height, window_size)

    # --- Selenium path ---
    use_custom_size = width and height
    if use_custom_size:
        window_size_arg = f"--window-size={width},{height}"
    else:
        window_size_arg = f"--window-size={window_size}"

    # Create browser-specific driver
    if driver_type == "firefox":
        driver = _create_firefox_driver(config, headless, width, height, window_size, use_custom_size)
    elif driver_type == "edge":
        driver = _create_edge_driver(config, headless, window_size_arg, use_custom_size)
    else:  # Default to Chrome
        driver = _create_chrome_driver(config, headless, no_sandbox, window_size_arg, use_custom_size)

    driver.implicitly_wait(5)
    return driver


# ═══════════════════════════════════════════════════════════════════════════════
# SELENIUM BROWSER FACTORIES
# ═══════════════════════════════════════════════════════════════════════════════

def _create_firefox_driver(config, headless, width, height, window_size, use_custom_size):
    """
    Create and configure a Firefox WebDriver instance.
    
    Uses GeckoDriver for browser automation. Will automatically download
    the driver if not found at the configured path.
    
    Args:
        config: ConfigParser with optional gecko_driver_path
        headless: Run in headless mode
        width/height: Custom window dimensions
        window_size: Default "width,height" string
        use_custom_size: Whether custom dimensions were specified
        
    Returns:
        Firefox WebDriver instance
    """
    path = config.get('Driver', 'gecko_driver_path', fallback=None) if config.has_section('Driver') else None
    if not path:
        path = DriverManager.ensure_driver("firefox")
        
    options = FirefoxOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument(f"--width={width or window_size.split(',')[0]}")
        options.add_argument(f"--height={height or window_size.split(',')[1]}")
    
    service = FirefoxService(executable_path=path) if path else FirefoxService()
    driver = webdriver.Firefox(service=service, options=options)
    
    if not headless and not use_custom_size:
        driver.maximize_window()
    elif use_custom_size:
        driver.set_window_size(int(width), int(height))
    
    return driver


def _create_edge_driver(config, headless, window_size_arg, use_custom_size):
    """
    Create and configure a Microsoft Edge WebDriver instance.
    
    Uses EdgeDriver (Chromium-based). Will automatically download
    the driver if not found at the configured path.
    
    Args:
        config: ConfigParser with optional edge_driver_path
        headless: Run in headless mode
        window_size_arg: Window size as "--window-size=W,H"
        use_custom_size: Whether custom dimensions were specified
        
    Returns:
        Edge WebDriver instance
    """
    path = config.get('Driver', 'edge_driver_path', fallback=None) if config.has_section('Driver') else None
    if not path:
        path = DriverManager.ensure_driver("edge")
        
    options = EdgeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument(window_size_arg)
    elif not use_custom_size:
        options.add_argument("--start-maximized")
    else:
        options.add_argument(window_size_arg)
    
    service = EdgeService(executable_path=path) if path else EdgeService()
    return webdriver.Edge(service=service, options=options)


def _create_chrome_driver(config, headless, no_sandbox, window_size_arg, use_custom_size):
    """
    Create and configure a Chrome WebDriver instance.
    
    Uses ChromeDriver for browser automation. Will automatically download
    the driver if not found at the configured path.
    
    Special Chrome Options:
    - --headless=new: Modern headless mode (Chrome 109+)
    - --no-sandbox: Required for Docker/CI environments
    - --disable-dev-shm-usage: Prevents shared memory issues
    - --disable-gpu: Prevents GPU-related crashes in headless
    
    Args:
        config: ConfigParser with optional chrome_driver_path
        headless: Run in headless mode
        no_sandbox: Disable Chrome sandbox (for CI)
        window_size_arg: Window size as "--window-size=W,H"
        use_custom_size: Whether custom dimensions were specified
        
    Returns:
        Chrome WebDriver instance
    """
    path = config.get('Driver', 'chrome_driver_path', fallback=None) if config.has_section('Driver') else None
    if not path:
        path = DriverManager.ensure_driver("chrome")
        
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # Modern headless mode
        options.add_argument(window_size_arg)
    elif not use_custom_size:
        options.add_argument("--start-maximized")
    else:
        options.add_argument(window_size_arg)

    if no_sandbox:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    
    options.add_argument("--disable-gpu")
    
    service = ChromeService(executable_path=path) if path else ChromeService()
    return webdriver.Chrome(service=service, options=options)


# ═══════════════════════════════════════════════════════════════════════════════
# PLAYWRIGHT DRIVER FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def get_playwright_driver(driver_type, headless, width, height, window_size):
    """
    Create a Playwright browser instance wrapped for Selenium compatibility.
    
    Playwright offers faster execution and better stability than Selenium
    for modern web applications. This function creates a Playwright Page
    and wraps it with PlaywrightWrapper to provide a Selenium-like API.
    
    Browser Mapping:
        - chrome → Chromium (with Chrome channel)
        - chromium → Chromium (generic)
        - firefox → Firefox
        - webkit → WebKit (Safari engine)
        - edge → Chromium (with Edge channel)
    
    Args:
        driver_type: Browser name (chrome, firefox, edge, webkit)
        headless: Run without visible window
        width/height: Custom viewport dimensions (or None)
        window_size: Default "width,height" string
        
    Returns:
        PlaywrightWrapper: Selenium-compatible wrapper around Playwright Page
        
    Raises:
        ImportError: If Playwright is not installed
        
    Notes:
        - Playwright browsers must be installed: `playwright install`
        - WebKit is only available with Playwright (not Selenium)
        - Chrome/Edge use their installed channels (not Chromium generic)
    """
    if sync_playwright is None:
        raise ImportError(
            "Playwright not installed. Install with:\n"
            "  pip install playwright\n"
            "  playwright install"
        )
    
    # Start Playwright and select browser engine
    playwright_instance = sync_playwright().start()
    
    browser_type_map = {
        "chrome": playwright_instance.chromium,
        "chromium": playwright_instance.chromium,
        "firefox": playwright_instance.firefox,
        "webkit": playwright_instance.webkit,
        "edge": playwright_instance.chromium  # Edge uses Chromium engine
    }
    
    browser_engine = browser_type_map.get(driver_type, playwright_instance.chromium)
    
    # Configure channel for specific browsers
    launch_args = {}
    if driver_type == "edge":
        launch_args["channel"] = "msedge"
    elif driver_type == "chrome":
        launch_args["channel"] = "chrome"

    # Launch browser
    browser = browser_engine.launch(headless=headless, **launch_args)
    
    # Configure viewport
    if width and height:
        viewport = {"width": int(width), "height": int(height)}
    else:
        w, h = window_size.split(',')
        viewport = {"width": int(w), "height": int(h)}
        
    # Create browser context and page
    context = browser.new_context(viewport=viewport)
    page = context.new_page()
    
    # Return Selenium-compatible wrapper
    from .playwright_wrapper import PlaywrightWrapper
    return PlaywrightWrapper(page, browser, playwright_instance)
