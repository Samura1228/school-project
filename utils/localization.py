import json
import os

# Load locales
LOCALES = {}
try:
    with open('data/locales.json', 'r', encoding='utf-8') as f:
        LOCALES = json.load(f)
except Exception as e:
    print(f"Error loading locales: {e}")

def get_text(key, lang='en', **kwargs):
    """
    Get translated text for a key.
    kwargs are used for string formatting (e.g., {username}).
    """
    if key not in LOCALES:
        return key
    
    text_dict = LOCALES[key]
    text = text_dict.get(lang, text_dict.get('en', key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
            
    return text