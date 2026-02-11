import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
from qa_framework.core.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        # Reset singleton between tests
        ConfigManager._instance = None
    
    def test_singleton_behavior(self):
        """Verify that ConfigManager follows the singleton pattern."""
        config1 = ConfigManager.instance()
        config2 = ConfigManager.instance()
        self.assertIs(config1, config2)
        
    def test_initialization_failure(self):
        """Verify that direct instantiation raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            ConfigManager()

    @patch("builtins.open", new_callable=mock_open, read_data="Driver:\n  type: firefox\n")
    @patch("os.path.exists", return_value=True)
    def test_load_base_yaml(self, mock_exists, mock_file):
        """Verify loading of config.yaml."""
        config = ConfigManager.instance()
        self.assertEqual(config.get("Driver.type"), "firefox")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.getenv")
    def test_env_specific_load(self, mock_getenv, mock_exists, mock_file):
        """Verify loading of config.{env}.yaml overrides base config."""
        # Setup mocks
        mock_getenv.return_value = "staging" # ENV=staging
        
        # We need to simulate multiple file opens: config.yaml and config.staging.yaml
        # Using a side_effect for open is cleaner when dealing with multiple files
        file_contents = {
            "config.yaml": "Driver:\n  type: chrome\n  timeout: 10",
            "config.staging.yaml": "Driver:\n  timeout: 30"
        }
        
        def side_effect_open(filename, mode='r'):
            # Simple matching strategy for mock
            content = ""
            if "config.yaml" in filename and "staging" not in filename:
                content = file_contents["config.yaml"]
            elif "config.staging.yaml" in filename:
                content = file_contents["config.staging.yaml"]
            return mock_open(read_data=content).return_value
            
        mock_file.side_effect = side_effect_open
        mock_exists.return_value = True # Assume files exist
        
        config = ConfigManager.instance()
        
        # Verify base value
        self.assertEqual(config.get("Driver.type"), "chrome")
        # Verify override value
        self.assertEqual(config.get("Driver.timeout"), 30)

    @patch("os.environ.get")
    def test_env_variable_override(self, mock_get):
        """Verify that environment variables override config values."""
        # Setup ConfigManager with some basic data
        with patch.object(ConfigManager, '_load_yaml'):
            config = ConfigManager.instance()
            config._config = {"Driver": {"type": "chrome"}}
            
            # Mock os.environ to have the override
            with patch.dict(os.environ, {"DRIVER_TYPE": "safari"}):
                self.assertEqual(config.get("Driver.type"), "safari")

    def test_get_nested_keys(self):
        """Verify dot notation access."""
        with patch.object(ConfigManager, '_load_yaml'):
            config = ConfigManager.instance()
            config._config = {
                "Server": {
                    "Database": {
                        "host": "localhost"
                    }
                }
            }
            self.assertEqual(config.get("Server.Database.host"), "localhost")
            self.assertIsNone(config.get("Server.Database.port"))
            self.assertEqual(config.get("Server.Database.port", 5432), 5432)

    def test_get_driver_config(self):
        """Verify convenience method for driver config."""
        with patch.object(ConfigManager, '_load_yaml'):
            config = ConfigManager.instance()
            config._config = {"Driver": {"type": "edge"}}
            driver_config = config.get_driver_config()
            self.assertEqual(driver_config["type"], "edge")

if __name__ == "__main__":
    unittest.main()
