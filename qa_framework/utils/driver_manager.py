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
    GECKO_DRIVER_URL = "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-win64.zip"
    EDGE_DRIVER_URL = "https://msedgedriver.azureedge.net/122.0.2365.59/edgedriver_win64.zip"
    
    @classmethod
    def get_chrome_download_url(cls):
        """Fetch the latest stable chromedriver URL for win64."""
        versions_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        try:
            response = requests.get(versions_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Get stable version downloads
                downloads = data.get('channels', {}).get('Stable', {}).get('downloads', {}).get('chromedriver', [])
                for download in downloads:
                    if download.get('platform') == 'win64':
                        return download.get('url')
        except Exception as e:
            # Important: show full exception name for diagnostics
            print(f"[DriverManager] Error fetching Chrome versions ({type(e).__name__}): {e}")
        
        # Fallback to 133 (current stable) if API fails to avoid the 122 mismatch
        return "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.53/win64/chromedriver-win64.zip"

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
        # To handle version mismatches, users should delete the drivers folder
        if os.path.exists(local_path):
            return local_path

        # If not, download and unzip
        if browser_type == "chrome":
            url = cls.get_chrome_download_url()
        elif browser_type == "firefox":
            url = cls.GECKO_DRIVER_URL
        else:
            url = cls.EDGE_DRIVER_URL
        
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
            
            # Set executable permissions
            st = os.stat(local_path)
            os.chmod(local_path, st.st_mode | stat.S_IEXEC)
            
            print(f"[DriverManager] {executable_name} successfully downloaded to {cls.DRIVERS_DIR}")
            return local_path
        else:
            raise Exception(f"Failed to download driver for {browser_type}. Status: {response.status_code}")
