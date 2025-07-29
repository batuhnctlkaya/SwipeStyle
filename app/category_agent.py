import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_specs_for_category(category):
    """
    Use Gemini to generate specs/questions for a new category.
    Returns a list of spec dicts, or None if generation fails or output is invalid.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (
            f"'{category}' kategorisi için Türkçe olarak 3-5 soru ve emoji öner. "
            "Her soru için bir anahtar (key), bir soru (question), bir emoji (emoji) içeren bir JSON listesi döndür.\n"
            """" Example Output: Headphones": {
    "specs": [
      {"key": "Kablosuz", "question": "Kablosuz kulaklık ister misiniz?", "emoji": "🎧"},
      {"key": "ANC", "question": "Aktif gürültü engelleme önemli mi?", "emoji": "🔇"},
      {"key": "Bass", "question": "Güçlü bass ister misiniz?", "emoji": "🎵"},
      {"key": "Mikrofon Kalitesi", "question": "Mikrofon kalitesi önemli mi?", "emoji": "🎤"},
      {"key": "Kulak İçi", "question": "Kulak içi mi tercih edersiniz?", "emoji": "👂"},
      {"key": "Kulak Üstü", "question": "Kulak üstü mü tercih edersiniz?", "emoji": "🦻"}
    ]
  },"""
        )
        response = model.generate_content(prompt)
        # Debug: Write prompt and output to output.txt
        # Try to pretty-print the output if it's valid JSON, else print raw
        try:
            parsed = json.loads(response.text)
            pretty_output = json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            pretty_output = response.text
        with open('output.txt', 'a', encoding='utf-8') as debug_file:
            debug_file.write(f"PROMPT:\n{prompt}\n\nOUTPUT:\n{pretty_output}\n{'='*40}\n")
        arr = None
        try:
            arr = json.loads(response.text)
        except Exception:
            # If Gemini output is not valid JSON, return None
            return None
        # Accept both list and dict with 'specs' key
        if isinstance(arr, list) and all(isinstance(x, dict) and 'key' in x and 'question' in x and 'emoji' in x for x in arr):
            return arr
        if isinstance(arr, dict):
            # If output is {"Category": {"specs": [...]}}
            for v in arr.values():
                if isinstance(v, dict) and 'specs' in v and isinstance(v['specs'], list):
                    specs = v['specs']
                    if all(isinstance(x, dict) and 'key' in x and 'question' in x and 'emoji' in x for x in specs):
                        return {'category_name': list(arr.keys())[0], 'specs': specs}
            # If output is {"specs": [...]}
            if 'specs' in arr and isinstance(arr['specs'], list):
                specs = arr['specs']
                if all(isinstance(x, dict) and 'key' in x and 'question' in x and 'emoji' in x for x in specs):
                    return {'category_name': category, 'specs': specs}
        return None
    except Exception as e:
        # Debug: Write exception to output.txt
        with open('output.txt', 'a', encoding='utf-8') as debug_file:
            debug_file.write(f"EXCEPTION:\n{str(e)}\n{'='*40}\n")
        # If Gemini API call fails, return None
        return None

class CategoryAgent:
    """
    Manages product categories for the recommendation system.
    - Loads and saves categories from/to categories.json
    - Checks if a category exists for a user query
    - If not, uses Gemini to generate specs and creates the category
    """
    def __init__(self, categories_path='categories.json'):
        self.categories_path = categories_path
        self._load_categories()

    def _load_categories(self):
        """Load categories from the JSON file, or initialize empty if not found."""
        if os.path.exists(self.categories_path):
            with open(self.categories_path, 'r', encoding='utf-8') as f:
                self.categories = json.load(f)
        else:
            self.categories = {}

    def _save_categories(self):
        """Save the current categories to the JSON file."""
        with open(self.categories_path, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)

    def get_or_create_category(self, user_query_or_category):
        """
        Given a user query or category name, return the matching category.
        If it doesn't exist, create it using Gemini and save to file.
        Returns (category_name, created: bool) or (None, False) if failed.
        """
        # Try to match user input to an existing category
        for cat in self.categories:
            if cat.lower() in user_query_or_category.lower() or user_query_or_category.lower() in cat.lower():
                return cat, False
        # If not found, create new category
        specs_result = generate_specs_for_category(user_query_or_category)
        if specs_result:
            # If specs_result is a dict with 'category_name' and 'specs', use that
            if isinstance(specs_result, dict) and 'category_name' in specs_result and 'specs' in specs_result:
                cat_name = specs_result['category_name']
                specs = specs_result['specs']
                self.categories[cat_name] = {"specs": specs}
                self._save_categories()
                return cat_name, True
            # If specs_result is a list, use the original category name
            elif isinstance(specs_result, list):
                self.categories[user_query_or_category] = {"specs": specs_result}
                self._save_categories()
                return user_query_or_category, True
        return None, False

    def get_categories(self):
        """Return a list of all category names."""
        return list(self.categories.keys())
