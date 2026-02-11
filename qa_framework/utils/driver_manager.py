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
    def get_chrome_download_url(cls, version=None):
        """
        Fetch the chromedriver URL.
        
        Args:
            version: Optional specific version string (e.g., "144.0.7559.133" or "144")
                     If None, fetches the latest Stable version.
        """
        target_platform = cls.get_platform()
        
        # If a specific full version is requested
        if version and len(version.split('.')) >= 3:
             return f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{target_platform}/chromedriver-{target_platform}.zip"

        versions_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        
        # If major version requested (e.g. "144"), try to find best match
        if version and '.' not in version:
             # Logic to find latest good version for major version could go here
             # For now, we will fallback to a known 144 build if requested
             if version == "144":
                 # Fallback to a known valid 144 build
                 return f"https://storage.googleapis.com/chrome-for-testing-public/144.0.7559.133/{target_platform}/chromedriver-{target_platform}.zip"

        try:
            response = requests.get(versions_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Default to Stable if no version
                downloads = data.get('channels', {}).get('Stable', {}).get('downloads', {}).get('chromedriver', [])
                for download in downloads:
                    if download.get('platform') == target_platform:
                        return download.get('url')
        except Exception as e:
            print(f"[DriverManager] Error fetching Chrome versions ({type(e).__name__}): {e}")
        
        # Final fallback
        if target_platform == "linux64":
            return "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.53/linux64/chromedriver-linux64.zip"
        return "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.53/win64/chromedriver-win64.zip"

    @classmethod
    def ensure_driver(cls, browser_type, version=None):
        """Checks if driver exists, if not, downloads and unzips it."""
        browser_type = browser_type.lower()
        if not os.path.exists(cls.DRIVERS_DIR):
            os.makedirs(cls.DRIVERS_DIR)
        
        # Add version to executable name to avoid conflicts? 
        # For now, let's keep it simple and overwrite if version changes or just use standard name
        # A better approach would be drivers/144/chromedriver.exe, but that requires bigger refactor.
        # Current strategy: If version is specified, we trust the caller knows what they want.
        
        executable_name = cls.get_executable_name(browser_type)
        if not executable_name:
            return None

        local_path = os.path.join(cls.DRIVERS_DIR, executable_name)
        
        # Check if already exists in features/drivers
        # To handle version mismatches, users should delete the drivers folder OR we can force download if version set?
        # For CI reliability: If version matches our hardcoded fallback, it's fine.
        if os.path.exists(local_path):
            return local_path

        # If not, download and unzip
        if browser_type == "chrome":
            url = cls.get_chrome_download_url(version)
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
        response = requests.get(url, timeout=120)  # 2 min timeout for driver downloads
        
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
