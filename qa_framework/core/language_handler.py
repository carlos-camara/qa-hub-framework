import os
import yaml
from typing import Any, Dict

class LanguageHandler:
    """
    Handles loading and resolving localized strings from YAML files.
    """
    
    def __init__(self, language_dir: str, default_lang: str = "en"):
        self.language_dir = language_dir
        self.current_lang = default_lang
        self.translations: Dict[str, Any] = {}
        self.load_language(default_lang)

    def load_language(self, lang: str):
        """Load translations from a YAML file."""
        # Try both .yaml and .yml extensions
        file_path = os.path.join(self.language_dir, f"{lang}.yaml")
        if not os.path.exists(file_path):
            file_path = os.path.join(self.language_dir, f"{lang}.yml")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations = yaml.safe_load(f) or {}
                self.current_lang = lang
            except Exception as e:
                print(f"Error loading translation file {file_path}: {e}")
                self.translations = {}
        else:
            print(f"Warning: Language file for '{lang}' not found in {self.language_dir}")

    def resolve(self, key: str) -> str:
        """
        Resolve a key (e.g., 'i18n:page.element.text') to its localized value.
        If key doesn't start with 'i18n:', return it as is.
        """
        if not key.startswith("i18n:"):
            return key
            
        # Strip prefix
        path = key[5:].split('.')
        
        value = self.translations
        for segment in path:
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            else:
                # Return the key if path is not found
                return key
        
        return str(value)
