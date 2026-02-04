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
    
    @classmethod
    def get_platform(cls):
        """Detect current platform and return Chrome-compatible platform name."""
        sys_platform = platform.system().lower()
        if sys_platform == "windows":
            return "win64"
        elif sys_platform == "linux":
            return "linux64"
        return "win64" # Default fallback

    @classmethod
    def get_executable_name(cls, browser_type):
        """Return the correct executable name for the current OS."""
        is_windows = platform.system().lower() == "windows"
        ext = ".exe" if is_windows else ""
        
        if browser_type == "chrome":
            return f"chromedriver{ext}"
        elif browser_type == "firefox":
            return f"geckodriver{ext}"
        elif browser_type == "edge":
            return f"msedgedriver{ext}"
        return None

    @classmethod
    def get_chrome_download_url(cls):
        """Fetch the latest chromedriver URL for the detected platform, checking multiple channels."""
        target_platform = cls.get_platform()
        versions_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        
        try:
            response = requests.get(versions_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                channels = data.get('channels', {})
                
                # We check channels in order of freshness to find the most capable version
                # Usually Stable is enough, but some users have Dev browsers
                for channel_name in ['Canary', 'Dev', 'Beta', 'Stable']:
                    channel_data = channels.get(channel_name)
                    if not channel_data:
                        continue
                        
                    downloads = channel_data.get('downloads', {}).get('chromedriver', [])
                    for download in downloads:
                        if download.get('platform') == target_platform:
                            print(f"[DriverManager] Found version {channel_data.get('version')} in {channel_name} channel")
                            return download.get('url')
                            
        except Exception as e:
            print(f"[DriverManager] Error fetching Chrome versions ({type(e).__name__}): {e}")
        
        # Fallback
        if target_platform == "linux64":
            return "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.53/linux64/chromedriver-linux64.zip"
        return "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.53/win64/chromedriver-win64.zip"

    @classmethod
    def ensure_driver(cls, browser_type):
        """Checks if driver exists, if not, downloads and unzips it."""
        browser_type = browser_type.lower()
        if not os.path.exists(cls.DRIVERS_DIR):
            os.makedirs(cls.DRIVERS_DIR)

        executable_name = cls.get_executable_name(browser_type)
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
            target = "win64" if cls.get_platform() == "win64" else "linux64"
            # Standard Firefox URLs usually contain platform strings
            url = f"https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-{target}.zip"
            if target == "linux64":
                 url = url.replace(".zip", ".tar.gz")
        else:
            # Edge is primarily Windows (simplified for now)
            url = "https://msedgedriver.azureedge.net/122.0.2365.59/edgedriver_win64.zip"
        
        print(f"[DriverManager] Downloading {browser_type} driver from {url}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            if url.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    # Handle nested directories in zips (like chromedriver-win64/chromedriver)
                    for member in zip_ref.namelist():
                        filename = os.path.basename(member)
                        if filename == executable_name:
                            # Extract only the executable to the drivers directory
                            with zip_ref.open(member) as source, open(local_path, "wb") as target:
                                target.write(source.read())
                            break
            elif url.endswith(".tar.gz"):
                 with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
                    for member in tar.getmembers():
                        filename = os.path.basename(member.name)
                        if filename == executable_name:
                            source = tar.extractfile(member)
                            with open(local_path, "wb") as target:
                                target.write(source.read())
                            break
            
            # Set executable permissions (crucial for Linux)
            st = os.stat(local_path)
            os.chmod(local_path, st.st_mode | stat.S_IEXEC)
            
            print(f"[DriverManager] {executable_name} successfully downloaded to {cls.DRIVERS_DIR}")
            return local_path
        else:
            raise Exception(f"Failed to download driver for {browser_type}. Status: {response.status_code}")
