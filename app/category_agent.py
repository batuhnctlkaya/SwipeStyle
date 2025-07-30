"""
SwipeStyle Kategori Agent Modülü
================================

Bu modül, SwipeStyle uygulamasının kategori yönetimi işlevlerini içerir.
Kategorileri yükler, kaydeder ve yeni kategoriler oluşturur.

Ana Sınıflar:
- CategoryAgent: Kategori yönetimi ana sınıfı

Fonksiyonlar:
- generate_specs_for_category: Yeni kategori için özellikler oluşturur

Özellikler:
- Kategori tespiti ve eşleştirme
- Gemini AI ile yeni kategori oluşturma
- JSON dosya yönetimi
- Debug log'ları

Gereksinimler:
- Google Generative AI (Gemini)
- categories.json dosyası
- .env dosyasında GEMINI_API_KEY
"""

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
    Gemini AI kullanarak yeni kategori için özellikler ve sorular oluşturur.
    
    Bu fonksiyon, Gemini AI'ya kategori adını gönderir ve o kategori
    için uygun sorular, emojiler ve anahtar kelimeler oluşturmasını ister.
    Sonuç JSON formatında döner ve debug için output.txt'ye yazılır.
    
    Args:
        category (str): Yeni kategori adı (örn: "Tablet")
        
    Returns:
        dict or list or None: Oluşturulan özellikler veya None
        
    Dönen Format:
        {
            "category_name": "Tablet",
            "specs": [
                {"key": "Ekran Boyutu", "question": "Büyük ekran ister misiniz?", "emoji": "📱"},
                {"key": "Depolama", "question": "Fazla depolama alanı ister misiniz?", "emoji": "💾"}
            ]
        }
        
    Örnek:
        >>> generate_specs_for_category("Tablet")
        {"category_name": "Tablet", "specs": [...]}
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
    SwipeStyle Kategori Yönetimi Ana Sınıfı
    
    Bu sınıf, ürün kategorilerini yönetir ve yeni kategoriler oluşturur.
    Kategorileri JSON dosyasından yükler, kaydeder ve kullanıcı sorgularına
    göre kategori eşleştirmesi yapar.
    
    Özellikler:
    - categories_path: Kategori dosyası yolu
    - categories: Yüklenen kategori sözlüğü
    
    Ana Metodlar:
    - get_or_create_category(): Kategori tespiti/oluşturma
    - _load_categories(): Kategorileri yükler
    - _save_categories(): Kategorileri kaydeder
    - get_categories(): Kategori listesi döner
    
    Kullanım:
        >>> agent = CategoryAgent()
        >>> category, created = agent.get_or_create_category("kablosuz kulaklık")
        >>> print(category, created)
        "Headphones" False
    """
    
    def __init__(self, categories_path='categories.json'):
        """
        CategoryAgent'ı başlatır.
        
        Args:
            categories_path (str): Kategori dosyasının yolu (varsayılan: 'categories.json')
        """
        self.categories_path = categories_path
        self._load_categories()

    def _load_categories(self):
        """
        Kategorileri JSON dosyasından yükler.
        
        Eğer dosya mevcut değilse, boş bir sözlük oluşturur.
        Bu metod, __init__ tarafından otomatik olarak çağrılır.
        """
        if os.path.exists(self.categories_path):
            with open(self.categories_path, 'r', encoding='utf-8') as f:
                self.categories = json.load(f)
        else:
            self.categories = {}

    def _save_categories(self):
        """
        Mevcut kategorileri JSON dosyasına kaydeder.
        
        Kategoriler UTF-8 encoding ile kaydedilir ve
        Türkçe karakterler korunur.
        """
        with open(self.categories_path, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)

    def get_or_create_category(self, user_query_or_category):
        """
        Kullanıcı sorgusuna göre kategori tespiti yapar veya yeni kategori oluşturur.
        
        Bu metod önce mevcut kategorilerde eşleşme arar. Eğer bulamazsa,
        Gemini AI kullanarak yeni kategori oluşturur ve dosyaya kaydeder.
        
        Args:
            user_query_or_category (str): Kullanıcı sorgusu veya kategori adı
            
        Returns:
            tuple: (category_name, created)
                - category_name (str): Tespit edilen/oluşturulan kategori adı
                - created (bool): Yeni oluşturuldu mu? (True/False)
                
        Örnek:
            >>> agent = CategoryAgent()
            >>> category, created = agent.get_or_create_category("kablosuz kulaklık")
            >>> print(f"Kategori: {category}, Yeni mi: {created}")
            Kategori: Headphones, Yeni mi: False
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
        """
        Tüm kategori adlarının listesini döndürür.
        
        Returns:
            list: Kategori adları listesi
            
        Örnek:
            >>> agent = CategoryAgent()
            >>> categories = agent.get_categories()
            >>> print(categories)
            ['Mouse', 'Headphones', 'Phone', 'Laptop']
        """
        return list(self.categories.keys())
