import os
import yaml
from typing import Any, Dict

class LanguageHandler:
    """
    Handles loading and resolving localized strings from YAML files.
    """
    
    def __init__(self, language_dir: str, default_lang: str = "en"):
        self.language_dir = language_dir
        # Extract base lang (e.g., 'en' from 'en_US.UTF-8')
        self.target_lang = default_lang.split('_')[0].split('.')[0].lower() if default_lang else "en"
        self.translations: Dict[str, Any] = {}
        self.load_translations()

    def load_translations(self):
        """Load all translations from the language directory."""
        if not os.path.exists(self.language_dir):
            print(f"Warning: Language directory not found: {self.language_dir}")
            return

        for filename in os.listdir(self.language_dir):
            if filename.endswith((".yaml", ".yml")):
                file_path = os.path.join(self.language_dir, filename)
                view_name = os.path.splitext(filename)[0]
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f) or {}
                        # Each file's content is nested under its view name (filename)
                        self.translations[view_name] = content
                except Exception as e:
                    print(f"Error loading translation file {file_path}: {e}")

    def resolve(self, key: str) -> str:
        """
        Resolve a key like '[LANG:dashboard.header.subtitle]' to its localized value.
        Supports both '[LANG:key.path]' and legacy 'i18n:key.path'.
        """
        if key.startswith("[LANG:") and key.endswith("]"):
            # Strip '[LANG:' and ']'
            path_str = key[6:-1]
        elif key.startswith("i18n:"):
            # Strip 'i18n:'
            path_str = key[5:]
        else:
            return key
            
        path = path_str.split('.')
        
        value = self.translations
        for segment in path:
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            else:
                # Return the key if path is not found
                return key
        
        # Leaf resolution: if value is a dict, get target_lang from it
        if isinstance(value, dict):
            if self.target_lang in value:
                return str(value[self.target_lang])
            # Fallback to 'en' if target_lang is missing
            elif 'en' in value:
                return str(value['en'])
            
        return str(value)
