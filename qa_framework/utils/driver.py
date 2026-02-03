import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver(headless=True, no_sandbox=True, window_size="1365,768"):
    """
    Creates and returns a Chrome webdriver instance with standard configuration.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    if no_sandbox:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    if window_size:
        options.add_argument(f"--window-size={window_size}")
    
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver
