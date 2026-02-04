import os
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from .driver_manager import DriverManager

import re

def resolve_config_variable(config, value):
    """
    Resolves patterns like {Section_Option} in a string using values from the config.
    Example: {Driver_type} -> 'chrome'
    """
    if not isinstance(value, str):
        return value
        
    pattern = r'\{(\w+)_(\w+)\}'
    
    def replacer(match):
        section = match.group(1)
        option = match.group(2)
        if config.has_section(section) and config.has_option(section, option):
            return config.get(section, option)
        return match.group(0) # Return original if not found
        
    return re.sub(pattern, replacer, value)

def get_config():
    """Reads configuration from features/config/properties.cfg if it exists."""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), 'features', 'config', 'properties.cfg')
    if os.path.exists(config_path):
        config.read(config_path)
    return config

def get_driver(headless=True, no_sandbox=True, window_size="1365,768"):
    """
    Creates and returns a webdriver instance based on properties.cfg or defaults.
    """
    config = get_config()
    driver_type = "chrome"
    width = None
    height = None
    
    if config.has_section('Driver'):
        driver_type = config.get('Driver', 'type', fallback='chrome').lower()
        if config.has_option('Driver', 'headless'):
            headless = config.getboolean('Driver', 'headless')
        
        # Read window dimensions from config if provided
        width = config.get('Driver', 'window_width', fallback=None)
        height = config.get('Driver', 'window_height', fallback=None)

    # Determine window size strategy
    use_custom_size = width and height
    if use_custom_size:
        window_size_arg = f"--window-size={width},{height}"
    else:
        window_size_arg = f"--window-size={window_size}"

    if driver_type == "firefox":
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
        
    elif driver_type == "edge":
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
        driver = webdriver.Edge(service=service, options=options)
        
    else:  # Default to Chrome
        path = config.get('Driver', 'chrome_driver_path', fallback=None) if config.has_section('Driver') else None
        if not path:
            path = DriverManager.ensure_driver("chrome")
            
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
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
        driver = webdriver.Chrome(service=service, options=options)

    driver.implicitly_wait(5)
    return driver
