"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                          Config Manager                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Centralized configuration management for the framework.                      ║
║  Loads settings from:                                                         ║
║  1. config.yaml (Base)                                                        ║
║  2. config.{env}.yaml (Environment override)                                  ║
║  3. .env file (Secrets)                                                       ║
║  4. Environment variables                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os
import yaml
import threading
from typing import Any, Dict, Optional
from dotenv import load_dotenv

class ConfigManager:
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls.__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initializes the configuration by loading from all sources."""
        self._config = {}
        self.env = os.getenv("ENV", "local").lower()
        
        # Define config directory path
        self.config_dir = os.path.join(os.getcwd(), 'features', 'config')

        # 1. Load Base Config (config.yaml)
        self._load_yaml("config.yaml")
        
        # 2. Load Environment Config (config.{env}.yaml)
        if self.env != "local":
            self._load_yaml(f"config.{self.env}.yaml")
            
        # 3. Load .env file (from project root)
        load_dotenv(override=True)

    def _load_yaml(self, filename: str):
        """Loads a YAML file and merges it into the config."""
        path = os.path.join(self.config_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        self._deep_merge(self._config, data)
            except Exception as e:
                print(f"[WARN] Failed to load {filename}: {e}")

    def _deep_merge(self, target: Dict, source: Dict):
        """Recursively merges source dict into target dict."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    # Legacy support removed as requested by user to unify logic

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value using dot notation (e.g., 'Driver.type').
        Also checks environment variables as overrides (e.g., DRIVER_TYPE).
        """
        # 1. Check Env Var (Upper case, underscore separated)
        env_key = key.replace('.', '_').upper()
        if env_key in os.environ:
            return os.environ[env_key]
            
        # 2. Walk the config dict
        keys = key.split('.')
        current = self._config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current

    def get_driver_config(self) -> Dict[str, Any]:
        """Returns the Driver configuration section."""
        return self._config.get('Driver', {})

    def reload(self):
        """Force reload configuration (useful for tests)."""
        self._initialize()
