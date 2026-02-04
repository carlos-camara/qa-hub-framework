import os
import requests
import zipfile
import tarfile
import io
import platform
import stat

class DriverManager:
    """Handles automatic downloading and unzipping of browser drivers."""
    
    DRIVERS_DIR = os.path.join(os.getcwd(), 'features', 'drivers')
    
    # Placeholder URLs - In a real scenario, these would resolve to the latest stable versions
    # For this implementation, we use direct links for common versions as an example
    CHROME_DRIVER_URL = "https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/win64/chromedriver-win64.zip"
    GECKO_DRIVER_URL = "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-win64.zip"
    EDGE_DRIVER_URL = "https://msedgedriver.azureedge.net/122.0.2365.59/edgedriver_win64.zip"

    @classmethod
    def ensure_driver(cls, browser_type):
        """Checks if driver exists, if not, downloads and unzips it."""
        browser_type = browser_type.lower()
        if not os.path.exists(cls.DRIVERS_DIR):
            os.makedirs(cls.DRIVERS_DIR)

        executable_name = "chromedriver.exe" if browser_type == "chrome" else \
                          "geckodriver.exe" if browser_type == "firefox" else \
                          "msedgedriver.exe" if browser_type == "edge" else None

        if not executable_name:
            return None

        local_path = os.path.join(cls.DRIVERS_DIR, executable_name)
        
        # Check if already exists in features/drivers
        if os.path.exists(local_path):
            return local_path

        # If not, download and unzip
        url = cls.CHROME_DRIVER_URL if browser_type == "chrome" else \
              cls.GECKO_DRIVER_URL if browser_type == "firefox" else \
              cls.EDGE_DRIVER_URL
        
        print(f"[DriverManager] Downloading {browser_type} driver from {url}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # Handle nested directories in zips (like chromedriver-win64/chromedriver.exe)
                for member in zip_ref.namelist():
                    filename = os.path.basename(member)
                    if filename == executable_name:
                        # Extract only the executable to the drivers directory
                        with zip_ref.open(member) as source, open(local_path, "wb") as target:
                            target.write(source.read())
                        break
            
            # Set executable permissions (especially for non-windows, but good practice)
            st = os.stat(local_path)
            os.chmod(local_path, st.st_mode | stat.S_IEXEC)
            
            print(f"[DriverManager] {executable_name} successfully downloaded to {cls.DRIVERS_DIR}")
            return local_path
        else:
            raise Exception(f"Failed to download driver for {browser_type}. Status: {response.status_code}")
