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
        # Extract base lang (e.g., 'en' from 'en_US.UTF-8' or 'en_GB')
        base_lang = lang.split('_')[0].split('.')[0].lower() if lang else "en"
        
        # Order of preference: full lang, then base lang
        langs_to_try = [lang, base_lang] if lang != base_lang else [base_lang]
        
        for l in langs_to_try:
            file_path = os.path.join(self.language_dir, f"{l}.yaml")
            if not os.path.exists(file_path):
                file_path = os.path.join(self.language_dir, f"{l}.yml")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations = yaml.safe_load(f) or {}
                    self.current_lang = l
                    return # Successfully loaded
                except Exception as e:
                    print(f"Error loading translation file {file_path}: {e}")
        
        print(f"Warning: No valid language file found for '{lang}' or '{base_lang}' in {self.language_dir}")

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
