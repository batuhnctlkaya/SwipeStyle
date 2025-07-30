"""
SwipeStyle Veritabanı Tabanlı Kategori Agent Modülü
==================================================

Bu modül, SwipeStyle uygulamasının kategori yönetimi işlevlerini veritabanı kullanarak gerçekleştirir.
SQLAlchemy modelleri kullanarak kategorileri yükler, kaydeder ve yeni kategoriler oluşturur.

Ana Sınıflar:
- DatabaseCategoryAgent: Veritabanı tabanlı kategori yönetimi ana sınıfı

Fonksiyonlar:
- generate_specs_for_category: Yeni kategori için özellikler oluşturur (category_agent.py'den kopyalandı)

Özellikler:
- SQLAlchemy ORM kullanımı
- Veritabanı transaction yönetimi
- Kategori tespiti ve eşleştirme
- Gemini AI ile yeni kategori oluşturma
- Debug log'ları

Gereksinimler:
- SQLAlchemy modelleri (models.py)
- Google Generative AI (Gemini)
- .env dosyasında GEMINI_API_KEY
"""

import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from app.models import db, Category, CategorySpec

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
            "Sadece JSON listesi döndür, başka hiçbir metin veya açıklama ekleme. "
            "Her soru için bir anahtar (key), bir soru (question), bir emoji (emoji) içeren bir JSON listesi döndür.\n"
            "Örnek format: "
            '[{"key": "Kablosuz", "question": "Kablosuz bağlantı ister misiniz?", "emoji": "📶"}]'
        )
        response = model.generate_content(prompt)
        
        # Clean the response text - remove markdown code blocks
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith('```'):
            response_text = response_text[3:]   # Remove ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove trailing ```
        response_text = response_text.strip()
        
        # Debug: Write prompt and output to output.txt
        try:
            parsed = json.loads(response_text)
            pretty_output = json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            pretty_output = response_text
        with open('output.txt', 'a', encoding='utf-8') as debug_file:
            debug_file.write(f"PROMPT:\n{prompt}\n\nCLEANED OUTPUT:\n{pretty_output}\n{'='*40}\n")
        
        arr = None
        try:
            arr = json.loads(response_text)
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

class DatabaseCategoryAgent:
    """
    SwipeStyle Veritabanı Tabanlı Kategori Yönetimi Ana Sınıfı
    
    Bu sınıf, ürün kategorilerini veritabanı kullanarak yönetir ve yeni kategoriler oluşturur.
    SQLAlchemy modelleri kullanarak kategorileri veritabanından yükler, kaydeder ve 
    kullanıcı sorgularına göre kategori eşleştirmesi yapar.
    
    Özellikler:
    - Veritabanı tabanlı kategori yönetimi
    - SQLAlchemy ORM kullanımı
    - Transaction güvenliği
    - Otomatik kategori oluşturma
    
    Ana Metodlar:
    - get_or_create_category(): Kategori tespiti/oluşturma
    - get_categories(): Kategori listesi döner
    - get_category_by_name(): İsme göre kategori getir
    - create_category_with_specs(): Yeni kategori ve özellikleri oluştur
    
    Kullanım:
        >>> agent = DatabaseCategoryAgent()
        >>> category, created = agent.get_or_create_category("kablosuz kulaklık")
        >>> print(category.name, created)
        "Headphones" False
    """
    
    def __init__(self):
        """
        DatabaseCategoryAgent'ı başlatır.
        
        Veritabanı bağlantısını kontrol eder ve gerekirse tabloları oluşturur.
        """
        pass

    def get_or_create_category(self, user_query_or_category, language="tr"):
        """
        Kullanıcı sorgusuna göre kategori tespiti yapar veya yeni kategori oluşturur.
        
        Bu metod önce veritabanında mevcut kategorilerde eşleşme arar. Eğer bulamazsa,
        Gemini AI kullanarak yeni kategori oluşturur ve veritabanına kaydeder.
        
        Args:
            user_query_or_category (str): Kullanıcı sorgusu veya kategori adı
            
        Returns:
            tuple: (category, created)
                - category (Category): Tespit edilen/oluşturulan kategori nesnesi
                - created (bool): Yeni oluşturuldu mu? (True/False)
                
        Örnek:
            >>> agent = DatabaseCategoryAgent()
            >>> category, created = agent.get_or_create_category("kablosuz kulaklık")
            >>> print(f"Kategori: {category.name}, Yeni mi: {created}")
            Kategori: Headphones, Yeni mi: False
        """
        # Mevcut kategorilerde eşleşme ara
        categories = Category.query.all()
        
        # Önce tam eşleşme ara
        for cat in categories:
            if cat.name.lower() == user_query_or_category.lower():
                return cat, False
        
        # Sonra kısmi eşleşme ara
        for cat in categories:
            if cat.name.lower() in user_query_or_category.lower() or user_query_or_category.lower() in cat.name.lower():
                return cat, False
        
        # Türkçe sorguları için özel eşleştirmeler
        query_lower = user_query_or_category.lower()
        for cat in categories:
            cat_lower = cat.name.lower()
            
            # Kulaklık tespiti
            if any(word in query_lower for word in ['kulaklık', 'kulaklığı', 'headphone', 'earphone', 'earbud']):
                if cat_lower == 'headphones':
                    return cat, False
            
            # Mouse tespiti
            if any(word in query_lower for word in ['mouse', 'fare', 'maus']):
                if cat_lower == 'mouse':
                    return cat, False
            
            # Phone tespiti  
            if any(word in query_lower for word in ['phone', 'telefon', 'mobil', 'cep']):
                if cat_lower == 'phone':
                    return cat, False
            
            # Laptop tespiti
            if any(word in query_lower for word in ['laptop', 'dizüstü', 'notebook', 'bilgisayar']):
                if cat_lower == 'laptop':
                    return cat, False
        
        # Eşleşme bulunamazsa, yeni kategori oluştur
        specs_result = generate_specs_for_category(user_query_or_category)
        if specs_result:
            try:
                # Kategori adını belirle
                if isinstance(specs_result, dict) and 'category_name' in specs_result:
                    cat_name = specs_result['category_name']
                    specs = specs_result['specs']
                elif isinstance(specs_result, list):
                    cat_name = user_query_or_category
                    specs = specs_result
                else:
                    return None, False
                
                # Yeni kategori oluştur
                category = Category(name=cat_name)
                db.session.add(category)
                db.session.flush()  # ID'yi al ama henüz commit etme
                
                # Özellikleri ekle
                for spec_data in specs:
                    spec = CategorySpec(
                        category_id=category.id,
                        key=spec_data['key'],
                        question=spec_data['question'],
                        emoji=spec_data['emoji']
                    )
                    db.session.add(spec)
                
                # Tüm değişiklikleri kaydet
                db.session.commit()
                return category, True
                
            except Exception as e:
                db.session.rollback()
                # Debug: Write exception to output.txt
                with open('output.txt', 'a', encoding='utf-8') as debug_file:
                    debug_file.write(f"DATABASE EXCEPTION:\n{str(e)}\n{'='*40}\n")
                return None, False
        
        return None, False

    def get_categories(self):
        """
        Tüm kategorileri veritabanından getirir.
        
        Returns:
            list: Category nesneleri listesi
            
        Örnek:
            >>> agent = DatabaseCategoryAgent()
            >>> categories = agent.get_categories()
            >>> for cat in categories:
            ...     print(cat.name)
            Mouse
            Headphones
            Phone
            Laptop
        """
        return Category.query.all()

    def get_category_by_name(self, name):
        """
        İsme göre kategori getirir.
        
        Args:
            name (str): Kategori adı
            
        Returns:
            Category or None: Bulunan kategori nesnesi veya None
            
        Örnek:
            >>> agent = DatabaseCategoryAgent()
            >>> category = agent.get_category_by_name("Headphones")
            >>> print(category.name if category else "Not found")
            Headphones
        """
        return Category.query.filter_by(name=name).first()

    def create_category_with_specs(self, name, specs):
        """
        Yeni kategori ve özelliklerini oluşturur.
        
        Args:
            name (str): Kategori adı
            specs (list): Özellik listesi [{"key": "", "question": "", "emoji": ""}]
            
        Returns:
            tuple: (category, success)
                - category (Category): Oluşturulan kategori nesnesi
                - success (bool): Başarılı mı?
                
        Örnek:
            >>> specs = [{"key": "Test", "question": "Test?", "emoji": "🧪"}]
            >>> category, success = agent.create_category_with_specs("TestCat", specs)
            >>> print(f"Success: {success}")
            Success: True
        """
        try:
            # Kategori zaten var mı kontrol et
            existing = Category.query.filter_by(name=name).first()
            if existing:
                return existing, False
            
            # Yeni kategori oluştur
            category = Category(name=name)
            db.session.add(category)
            db.session.flush()  # ID'yi al
            
            # Özellikleri ekle
            for spec_data in specs:
                spec = CategorySpec(
                    category_id=category.id,
                    key=spec_data['key'],
                    question=spec_data['question'],
                    emoji=spec_data['emoji']
                )
                db.session.add(spec)
            
            db.session.commit()
            return category, True
            
        except Exception as e:
            db.session.rollback()
            # Debug: Write exception to output.txt
            with open('output.txt', 'a', encoding='utf-8') as debug_file:
                debug_file.write(f"CREATE CATEGORY EXCEPTION:\n{str(e)}\n{'='*40}\n")
            return None, False

    def get_categories_dict(self, language="tr"):
        """
        Kategorileri eski JSON formatına uygun sözlük olarak döndürür.
        
        Bu metod, eski API ile uyumluluğu korumak için kullanılır.
        Dil desteği eklenmiştir.
        
        Args:
            language (str): Dil kodu ("tr" veya "en")
        
        Returns:
            dict: JSON formatında kategori sözlüğü
            
        Format:
            {
                "Mouse": {
                    "specs": [
                        {"key": "Kablosuz", "question": "...", "emoji": "🖱️"}
                    ]
                }
            }
        """
        categories = self.get_categories()
        result = {}
        for category in categories:
            result[category.name] = {
                "specs": [spec.to_dict(language) for spec in category.specs]
            }
        return result

    def get_shopping_recommendations(self, query, country="TR", language="tr"):
        """
        Mock shopping önerileri döndürür (Google Shopping için).
        
        Args:
            query (str): Arama sorgusu
            country (str): Ülke kodu
            language (str): Dil kodu
            
        Returns:
            dict: Mock ürün önerileri
        """
        # Currency mapping
        currency_map = {
            "TR": "₺",
            "US": "$", 
            "GB": "£",
            "DE": "€",
            "FR": "€"
        }
        
        currency = currency_map.get(country, "$")
        
        # Product templates
        if language == "tr":
            templates = [
                f"Profesyonel {query.title()} - Model A",
                f"Kaliteli {query.title()} - Model B", 
                f"Ekonomik {query.title()} - Model C"
            ]
            stores = ["teknosa.com", "hepsiburada.com", "trendyol.com"]
        else:
            templates = [
                f"Premium {query.title()} - Model A",
                f"Professional {query.title()} - Model B",
                f"Budget {query.title()} - Model C"
            ]
            stores = ["amazon.com", "bestbuy.com", "ebay.com"]
        
        mock_products = []
        for i, (template, store) in enumerate(zip(templates, stores)):
            price = f"{currency}{299 - i*100}"
            mock_products.append({
                "title": template,
                "price": price,
                "source": store,
                "link": f"https://{store}/product{i+1}",
                "image": f"https://via.placeholder.com/200x200?text=Product+{i+1}",
                "rating": 4.5 - i*0.3,
                "reviews": 1250 - i*400,
                "position": i+1
            })
        
        return {
            "query": query,
            "country": country,
            "language": language,
            "total_results": len(mock_products),
            "products": mock_products
        }

    def save_user_settings(self, session_id, language, country):
        """
        Kullanıcı ayarlarını kaydeder.
        
        Args:
            session_id (str): Oturum ID'si
            language (str): Dil tercihi
            country (str): Ülke tercihi
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            from app.models import UserSettings
            
            # Mevcut ayarları ara
            settings = UserSettings.query.filter_by(session_id=session_id).first()
            
            if settings:
                # Güncelle
                settings.language = language
                settings.country = country
            else:
                # Yeni oluştur
                settings = UserSettings(
                    session_id=session_id,
                    language=language,
                    country=country
                )
                db.session.add(settings)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            with open('output.txt', 'a', encoding='utf-8') as debug_file:
                debug_file.write(f"SETTINGS SAVE ERROR:\n{str(e)}\n{'='*40}\n")
            return False

    def get_user_settings(self, session_id):
        """
        Kullanıcı ayarlarını getirir.
        
        Args:
            session_id (str): Oturum ID'si
            
        Returns:
            dict: Kullanıcı ayarları
        """
        try:
            from app.models import UserSettings
            
            settings = UserSettings.query.filter_by(session_id=session_id).first()
            
            if settings:
                return {
                    "session_id": settings.session_id,
                    "language": settings.language,
                    "country": settings.country
                }
            else:
                # Varsayılan ayarlar
                return {
                    "session_id": session_id,
                    "language": "tr",
                    "country": "TR"
                }
                
        except Exception as e:
            with open('output.txt', 'a', encoding='utf-8') as debug_file:
                debug_file.write(f"SETTINGS GET ERROR:\n{str(e)}\n{'='*40}\n")
            return {
                "session_id": session_id,
                "language": "tr",
                "country": "TR"
            }

    def get_supported_countries(self):
        """Desteklenen ülke listesini döndürür"""
        return {
            "TR": "Türkiye",
            "US": "United States", 
            "GB": "United Kingdom",
            "DE": "Germany",
            "FR": "France"
        }
    
    def get_supported_languages(self):
        """Desteklenen dil listesini döndürür"""
        return {
            "tr": "Türkçe",
            "en": "English"
        }
