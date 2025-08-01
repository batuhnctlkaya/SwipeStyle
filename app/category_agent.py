"""
Geliştirilmiş Veritabanı Tabanlı Kategori Yöneticisi
===================================================

Bu modül, kategorilerin veritabanında saklanması ve yönetilmesini sağlar.
Gemini AI ile otomatik kategori oluşturma, çoklu dil desteği ve Google Shopping entegrasyonu sunar.

Ana Özellikler:
- SQLAlchemy ile veritabanı yönetimi
- Gemini AI ile otomatik kategori ve soru oluşturma
- Türkçe ve İngilizce dil desteği
- Google Shopping entegrasyonu
- Akıllı kategori eşleştirme
- Çeviri servisi entegrasyonu

Sınıflar:
- EnhancedDatabaseCategoryAgent: Geliştirilmiş kategori yönetim sınıfı

Kullanım:
    agent = EnhancedDatabaseCategoryAgent()
    category, created = agent.get_or_create_category("kablosuz kulaklık", language="tr")
    categories = agent.get_categories_dict(language="en")
    products = agent.get_shopping_recommendations("laptop", "TR", "tr")
"""

import json
import re
import os
import google.generativeai as genai
from typing import Optional, Tuple, Dict, List
from app.models import db, Category, CategorySpec, UserSettings
from app.shopping_api import GoogleShoppingAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDatabaseCategoryAgent:
    """
    Geliştirilmiş veritabanı tabanlı kategori yöneticisi.
    
    Bu sınıf kategorilerin veritabanında saklanması, yönetilmesi ve
    Gemini AI ile otomatik oluşturulması işlemlerini gerçekleştirir.
    Çoklu dil desteği ve Google Shopping entegrasyonu içerir.
    """
    
    def __init__(self):
        """
        EnhancedDatabaseCategoryAgent'ı başlatır.
        
        Gemini AI'ı konfigüre eder ve çeviri servisi ile shopping API'sını başlatır.
        """
        # Gemini AI konfigürasyonu
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # Changed to 1.5-flash for higher quota
        else:
            logger.error("GEMINI_API_KEY environment variable bulunamadı!")
            self.model = None
        
        # Rate limiting for Gemini API
        self.last_api_call = 0
        self.api_call_interval = 2  # Reduced interval for 1.5-flash (much higher quota)
        
        # Çeviri servisi ve shopping API
        self.shopping_api = GoogleShoppingAPI()
        
        # Türkçe kategori anahtar kelimeleri (genişletilmiş)
        self.turkish_keywords = {
            'phones': ['telefon', 'akıllı telefon', 'smartphone', 'cep telefonu', 'mobil', 'iphone', 'android'],
            'laptops': ['laptop', 'bilgisayar', 'notebook', 'dizüstü', 'macbook', 'ultrabook'],
            'headphones': ['kulaklık', 'kablosuz kulaklık', 'bluetooth kulaklık', 'kulak içi', 'kulak üstü', 'airpods'],
            'tablets': ['tablet', 'ipad', 'android tablet', 'dokunmatik tablet'],
            'smartwatches': ['akıllı saat', 'smart watch', 'apple watch', 'samsung watch', 'fitness tracker'],
            'cameras': ['kamera', 'fotoğraf makinesi', 'video kamera', 'dslr', 'mirrorless'],
            'keyboards': ['klavye', 'mekanik klavye', 'gaming klavye', 'wireless klavye'],
            'mice': ['mouse', 'fare', 'gaming mouse', 'wireless mouse', 'bluetooth mouse'],
            'monitors': ['monitör', 'ekran', 'gaming monitör', '4k monitör', 'ultrawide'],
            'speakers': ['hoparlör', 'bluetooth hoparlör', 'speaker', 'ses sistemi'],
            'printers': ['yazıcı', 'printer', 'lazer yazıcı', 'inkjet yazıcı'],
            'routers': ['modem', 'router', 'wifi router', 'ağ cihazı'],
            'drones': ['drone', 'quadcopter', 'uav', 'drön'],
            'gaming': ['oyun', 'gaming', 'playstation', 'xbox', 'nintendo'],
            'storage': ['harddisk', 'ssd', 'usb', 'flash disk', 'external disk']
        }
    
    def _wait_for_rate_limit(self):
        """Rate limiting için bekleme yapar."""
        import time
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.api_call_interval:
            wait_time = self.api_call_interval - time_since_last_call
            logger.info(f"Rate limit koruması: {wait_time:.1f} saniye bekleniyor...")
            time.sleep(wait_time)
        
        self.last_api_call = time.time()
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Gemini AI kullanarak metin çevirisi yapar.
        
        Args:
            text (str): Çevrilecek metin
            source_lang (str): Kaynak dil kodu
            target_lang (str): Hedef dil kodu
            
        Returns:
            str: Çevrilmiş metin
        """
        if not self.model:
            logger.warning("Gemini model not available, returning original text")
            return text
            
        # Rate limiting
        self._wait_for_rate_limit()
            
        try:
            lang_names = {
                'tr': 'Turkish',
                'en': 'English'
            }
            
            source_name = lang_names.get(source_lang, source_lang)
            target_name = lang_names.get(target_lang, target_lang)
            
            prompt = f"""Translate the following text from {source_name} to {target_name}.
            Provide only the translation, no additional text or explanation.
            
            Text to translate: {text}
            
            Translation:"""
            
            response = self.model.generate_content(prompt)
            translation = response.text.strip()
            
            logger.info(f"Translated '{text}' from {source_lang} to {target_lang}: '{translation}'")
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Fallback to original text
    
    def get_or_create_category(self, user_query: str, language: str = "tr") -> Tuple[Optional[Category], bool]:
        """
        Kullanıcı sorgusuna göre kategori bulur veya oluşturur.
        
        Args:
            user_query (str): Kullanıcının arama sorgusu
            language (str): Dil kodu ("tr" veya "en")
            
        Returns:
            Tuple[Optional[Category], bool]: (Kategori objesi, oluşturuldu mu?)
            
        Örnekler:
            # Mevcut kategori
            category, created = agent.get_or_create_category("kablosuz kulaklık")
            # created = False
            
            # Yeni kategori
            category, created = agent.get_or_create_category("robot süpürge")  
            # created = True
        """
        try:
            # Önce mevcut kategorilerde ara
            existing_category = self._find_existing_category(user_query, language)
            if existing_category:
                logger.info(f"Mevcut kategori bulundu: {existing_category.name}")
                return existing_category, False
            
            # Yeni kategori oluştur
            new_category = self._create_new_category(user_query, language)
            if new_category:
                logger.info(f"Yeni kategori oluşturuldu: {new_category.name}")
                return new_category, True
            
            logger.error(f"Kategori oluşturulamadı: {user_query}")
            return None, False
            
        except Exception as e:
            logger.error(f"get_or_create_category hatası: {str(e)}")
            return None, False
    
    def _find_existing_category(self, user_query: str, language: str) -> Optional[Category]:
        """
        Mevcut kategorilerde eşleşme arar.
        
        Args:
            user_query (str): Kullanıcı sorgusu
            language (str): Dil kodu
            
        Returns:
            Optional[Category]: Bulunan kategori veya None
        """
        query_lower = user_query.lower()
        
        # Tüm kategorileri al
        all_categories = Category.query.all()
        
        # Direkt isim eşleşmesi
        for category in all_categories:
            if category.name.lower() in query_lower or query_lower in category.name.lower():
                return category
        
        # Türkçe anahtar kelime eşleşmesi
        if language == "tr":
            for category_type, keywords in self.turkish_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    # Bu anahtar kelimeye uygun kategori var mı?
                    for category in all_categories:
                        if category_type.lower() in category.name.lower():
                            return category
        
        # İngilizce için benzer mantık
        elif language == "en":
            english_keywords = {
                'phone': ['phone', 'smartphone', 'mobile', 'iphone', 'android'],
                'laptop': ['laptop', 'computer', 'notebook', 'macbook'],
                'headphone': ['headphone', 'earphone', 'bluetooth', 'wireless', 'airpods'],
                'tablet': ['tablet', 'ipad'],
                'watch': ['watch', 'smartwatch', 'apple watch'],
                'camera': ['camera', 'dslr', 'mirrorless'],
                'keyboard': ['keyboard', 'mechanical', 'gaming'],
                'mouse': ['mouse', 'gaming mouse'],
                'monitor': ['monitor', 'display', 'screen'],
                'speaker': ['speaker', 'bluetooth speaker'],
                'printer': ['printer', 'laser', 'inkjet'],
                'router': ['router', 'modem', 'wifi'],
                'drone': ['drone', 'quadcopter'],
                'gaming': ['gaming', 'playstation', 'xbox', 'nintendo'],
                'storage': ['storage', 'harddisk', 'ssd', 'usb']
            }
            
            for category_type, keywords in english_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    for category in all_categories:
                        if category_type.lower() in category.name.lower():
                            return category
        
        return None
    
    def _create_new_category(self, user_query: str, language: str) -> Optional[Category]:
        """
        Gemini AI kullanarak yeni kategori oluşturur.
        
        Args:
            user_query (str): Kullanıcı sorgusu
            language (str): Dil kodu
            
        Returns:
            Optional[Category]: Oluşturulan kategori veya None
        """
        if not self.model:
            logger.error("Gemini AI model bulunamadı, kategori oluşturulamıyor")
            return None
        
        try:
            # Kategori adı üretmek için prompt
            category_prompt = f"""
            Kullanıcı şu ürünü arıyor: "{user_query}"
            
            Bu ürün için uygun bir kategori adı öner. Kategori adı:
            - İngilizce olmalı (örn: "Headphones", "Laptops", "Gaming Chairs")
            - Tek kelime veya iki kelime olabilir
            - Genel bir kategori olmalı (çok spesifik olmamalı)
            - E-ticaret sitelerinde kullanılan standart kategori adları olmalı
            
            Sadece kategori adını ver, başka hiçbir şey yazma.
            """
            
            response = self.model.generate_content(category_prompt)
            if not response or not response.text:
                return None
            
            category_name = response.text.strip()
            # Temizlik
            category_name = re.sub(r'[^a-zA-Z\s]', '', category_name).strip()
            
            if not category_name:
                return None
            
            # Kategori varsa döndür
            existing = Category.query.filter_by(name=category_name).first()
            if existing:
                return existing
            
            # Yeni kategori oluştur
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()  # ID'yi al
            
            # Sorular oluştur
            specs = self.generate_specs_for_category(category_name, language)
            
            # Sorular varsa ekle
            if specs:
                for spec_data in specs:
                    question_tr = spec_data.get('question_tr', spec_data.get('question', ''))
                    
                    spec = CategorySpec(
                        category_id=category.id,
                        key=spec_data.get('key', ''),
                        question=question_tr,  # Set legacy question field
                        question_tr=question_tr,
                        question_en=spec_data.get('question_en', None),
                        emoji=spec_data.get('emoji', '❓'),
                        question_type='yesno',  # Always yesno
                        options=None  # Always None for yesno questions
                    )
                    db.session.add(spec)
            
            db.session.commit()
            return category
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Kategori oluşturma hatası: {str(e)}")
            return None

    def generate_specs_for_category(self, category_name: str, language: str = "tr") -> List[Dict]:
        """
        Gemini AI kullanarak kategori için sorular oluşturur.
        
        Args:
            category_name (str): Kategori adı
            language (str): Dil kodu
            
        Returns:
            List[Dict]: Oluşturulan sorular listesi
        """
        if not self.model:
            return []
        
        try:
            prompt = f"""
            "{category_name}" kategorisi için ürün filtreleme soruları oluştur.
            
            Kurallar:
            - 4-5 soru olsun
            - Soruları {language} dilinde yaz
            - Her soru için uygun emoji ekle
            - JSON formatında döndür
            - Sorular SADECE Yes/No tipinde olmalı
            - Her soru "Evet" veya "Hayır" ile cevaplanabilir olmalı
            - Açık uçlu veya çoktan seçmeli sorular yazmayın
            
            Format:
            [
                {{"key": "Wireless", "question": "Kablosuz olmasını ister misiniz?", "emoji": "📶"}},
                {{"key": "Budget", "question": "Bütçeniz 1000 TL altında mı?", "emoji": "💰"}},
                {{"key": "Portable", "question": "Taşınabilir olmasını istiyor musunuz?", "emoji": "🎒"}}
            ]
            
            ÖNEMLI: Tüm sorular "mı/mi", "musunuz", "ister misiniz" gibi Yes/No cevap gerektiren yapıda olmalı.
            """
            
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                return []
            
            # Markdown temizliği
            clean_text = response.text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            specs = json.loads(clean_text)
            
            # Çift dil desteği ekle
            if language == "tr":
                # Türkçe sorular İngilizceye çevir
                for spec in specs:
                    if "question" in spec:
                        spec["question_tr"] = spec["question"]
                        spec["question_en"] = self.translate_text(spec["question"], "tr", "en")
            
            elif language == "en":
                # İngilizce sorular Türkçeye çevir
                for spec in specs:
                    if "question" in spec:
                        spec["question_en"] = spec["question"]
                        spec["question_tr"] = self.translate_text(spec["question"], "en", "tr")
            
            return specs
            
        except Exception as e:
            logger.error(f"Soru oluşturma hatası: {str(e)}")
            return []
    
    def get_categories_dict(self, language: str = "tr") -> Dict:
        """
        Kategorileri JSON formatında döndürür.
        
        Args:
            language (str): Dil kodu
            
        Returns:
            Dict: Kategori sözlüğü
        """
        categories = Category.query.all()
        result = {}
        
        for category in categories:
            result[category.name] = category.to_dict(language)
        
        return result
    
    def get_categories(self, language: str = "tr") -> List[Dict]:
        """
        Kategorileri liste formatında döndürür (API için).
        
        Args:
            language (str): Dil kodu
            
        Returns:
            List[Dict]: Kategori listesi [{"name": "...", "emoji": "..."}, ...]
        """
        categories = Category.query.all()
        result = []
        
        for category in categories:
            category_dict = category.to_dict(language)
            result.append({
                "name": category.name,
                "emoji": category_dict.get("emoji", "📱")
            })
        
        return result
    
    def get_shopping_recommendations(self, query: str, country: str = "TR", language: str = "tr") -> Dict:
        """
        Google Shopping'ten ürün önerileri getirir.
        
        Args:
            query (str): Arama sorgusu
            country (str): Ülke kodu
            language (str): Dil kodu
            
        Returns:
            Dict: Ürün önerileri
        """
        try:
            products = self.shopping_api.search_products(query, country, language, max_results=8)
            
            return {
                "query": query,
                "country": country,
                "language": language,
                "total_results": len(products),
                "products": products
            }
        
        except Exception as e:
            logger.error(f"Shopping recommendations hatası: {str(e)}")
            return {
                "query": query,
                "country": country,
                "language": language,
                "total_results": 0,
                "products": [],
                "error": str(e)
            }
    
    def save_user_settings(self, session_id: str, language: str, country: str) -> bool:
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
            logger.error(f"Ayar kaydetme hatası: {str(e)}")
            return False
    
    def get_user_settings(self, session_id: str) -> Dict:
        """
        Kullanıcı ayarlarını getirir.
        
        Args:
            session_id (str): Oturum ID'si
            
        Returns:
            Dict: Kullanıcı ayarları
        """
        try:
            settings = UserSettings.query.filter_by(session_id=session_id).first()
            
            if settings:
                return settings.to_dict()
            else:
                # Varsayılan ayarlar
                return {
                    "session_id": session_id,
                    "language": "tr",
                    "country": "TR"
                }
                
        except Exception as e:
            logger.error(f"Ayar getirme hatası: {str(e)}")
            return {
                "session_id": session_id,
                "language": "tr",
                "country": "TR"
            }
    
    def save_user_settings(self, session_id: str, language: str = "tr", country: str = "TR") -> Dict:
        """
        Kullanıcı ayarlarını kaydeder.
        
        Args:
            session_id (str): Oturum ID'si
            language (str): Dil kodu
            country (str): Ülke kodu
            
        Returns:
            Dict: Kaydedilen ayarlar
        """
        try:
            settings = UserSettings.query.filter_by(session_id=session_id).first()
            
            if settings:
                settings.language = language
                settings.country = country
            else:
                settings = UserSettings(
                    session_id=session_id,
                    language=language,
                    country=country
                )
                db.session.add(settings)
            
            db.session.commit()
            
            return settings.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ayar kaydetme hatası: {str(e)}")
            return {
                "session_id": session_id,
                "language": "tr",
                "country": "TR"
            }
    
    def handle(self, data: Dict, language: str = "tr", session_id: str = None) -> Dict:
        """
        Soru-cevap akışını yönetir.
        
        Args:
            data (Dict): İstek verisi
            language (str): Dil kodu
            session_id (str): Oturum ID'si
            
        Returns:
            Dict: Yanıt verisi
        """
        try:
            step = data.get('step', 0)
            category_name = data.get('category', '')
            answers = data.get('answers', [])
            
            if not category_name:
                return {'error': 'Category name is required'}
            
            # Kategoriyi bul veya oluştur
            category, created = self.get_or_create_category(category_name, language)
            
            if not category:
                return {'error': 'Failed to find or create category'}
            
            category_dict = category.to_dict(language)
            specs = category_dict.get('specs', [])
            
            # Step 0-based indexing için step'i kontrol et
            if step < len(specs) and step >= 0:
                # Sonraki soruyu döndür
                spec = specs[step]
                
                # Always use Yes/No options
                options = ['Evet', 'Hayır'] if language == 'tr' else ['Yes', 'No']
                
                return {
                    'question': spec.get('question', ''),
                    'options': options,
                    'emoji': spec.get('emoji', '📱'),
                    'step': step
                }
            else:
                # Tüm sorular cevaplandı - Gemini AI ile öneriler üret
                selected_specs = []
                
                # Kullanıcının "Evet"/"Yes" dediği özellikleri topla
                for i, answer in enumerate(answers):
                    if i < len(specs):
                        if (language == 'tr' and answer == 'Evet') or (language == 'en' and answer == 'Yes'):
                            selected_specs.append(specs[i].get('key', ''))
                
                # Gemini AI ile ürün önerileri al
                try:
                    recommendations = self._generate_gemini_recommendations(category_name, selected_specs, language)
                    return {'recommendations': recommendations}
                except Exception as e:
                    logger.error(f"Gemini recommendation error: {e}")
                    # Fallback to mock data if Gemini fails
                    return {
                        'recommendations': [
                            {
                                'name': f'Recommended {category_name} 1',
                                'price': '$99.99',
                                'rating': 4.5,
                                'image': 'https://via.placeholder.com/200x200'
                            },
                            {
                                'name': f'Recommended {category_name} 2', 
                                'price': '$129.99',
                                'rating': 4.7,
                                'image': 'https://via.placeholder.com/200x200'
                            }
                        ]
                    }
                
        except Exception as e:
            logger.error(f"Handle error: {e}")
            return {'error': 'Failed to process request'}
    
    def _generate_gemini_recommendations(self, category: str, selected_specs: List[str], language: str = "tr") -> List[Dict]:
        """
        Gemini AI kullanarak ürün önerileri üretir.
        
        Args:
            category (str): Ürün kategorisi
            selected_specs (List[str]): Kullanıcının seçtiği özellikler
            language (str): Dil kodu
            
        Returns:
            List[Dict]: Ürün önerileri listesi
        """
        try:
            if not self.model:
                logger.error("Gemini model bulunamadı")
                return self._get_fallback_recommendations(category)
            
            # Rate limiting koruması
            self._wait_for_rate_limit()
            
            prompt = self._build_recommendation_prompt(category, selected_specs, language)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                recommendations = self._parse_gemini_response(response.text, category)
                print(recommendations)
                return recommendations
            else:
                logger.error("Gemini'den boş yanıt alındı")
                return self._get_fallback_recommendations(category)
                
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning(f"Gemini API günlük limitine ulaşıldı (50 istek/gün). Shopping API kullanılacak: {category}")
            else:
                logger.error(f"Gemini recommendation hatası: {e}")
            return self._get_fallback_recommendations(category)
    
    def _build_recommendation_prompt(self, category: str, selected_specs: List[str], language: str) -> str:
        """
        Gemini AI için ürün önerisi prompt'u oluşturur.
        
        Args:
            category (str): Ürün kategorisi
            selected_specs (List[str]): Seçilen özellikler
            language (str): Dil kodu
            
        Returns:
            str: Hazırlanmış prompt
        """
        specs_str = ', '.join(selected_specs) if selected_specs else "temel özellikler"
        
        if language == 'tr':
            prompt = (
                f"Türk pazarında '{category}' kategorisinde, şu özelliklere sahip ürünler öner: {specs_str}. "
                "Her ürün için isim, FIYAT (TL cinsinden) ve kısa açıklama ver. "
                "5 ürün öner. Sadece aşağıdaki örnekteki gibi kısa bir liste olarak dön.\n\n"
                "Örnek çıktı:\n"
                "Sony WH-1000XM4 - FIYAT - Kablosuz, noise cancelling\n"
                "Apple AirPods Pro - FIYAT - True wireless, ANC\n\n"
                "Lütfen sadece bu formatta dön: Ürün Adı - Fiyat - Kısa Açıklama."
            )
        else:
            prompt = (
                f"Recommend products in the '{category}' category with these features: {specs_str}. "
                "For each product, provide name, estimated price (in USD), and brief description. "
                "Recommend 5 products. Return as a simple list like the example below.\n\n"
                "Example output:\n"
                "Sony WH-1000XM4 - $350 - Wireless, noise cancelling\n"
                "Apple AirPods Pro - $250 - True wireless, ANC\n\n"
                "Please return only in this format: Product Name - Price - Brief Description."
            )
        
        return prompt
    
    def _parse_gemini_response(self, text: str, category: str) -> List[Dict]:
        """
        Gemini AI yanıtını ayrıştırır ve ürün önerilerini formatlar.
        
        Args:
            text (str): Gemini AI'dan gelen ham yanıt
            category (str): Ürün kategorisi
            
        Returns:
            List[Dict]: Formatlanmış ürün önerileri
        """
        import re
        lines = text.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if not line or 'Fiyat' in line or 'Price' in line or line.startswith('#'):
                continue
                
            # Satırı ayrıştır: Ürün Adı - Fiyat - Açıklama
            parts = [p.strip() for p in re.split(r'-', line) if p.strip()]
            
            if len(parts) >= 2:
                name = parts[0]
                price = parts[1]
                description = parts[2] if len(parts) > 2 else ""
                
                # Fiyattan sayısal değeri çıkar
                price_match = re.search(r'[\d,]+', price)
                if price_match:
                    price_num = price_match.group()
                else:
                    price_num = "N/A"
                
                # Akakce arama linki oluştur
                search_query = re.sub(r'[^\w\s]', '', name)
                search_query = re.sub(r'\s+', '+', search_query)
                link = f'https://www.google.com/search?q={search_query}'
                
                recommendations.append({
                    'name': name,
                    'price': price,
                    'description': description,
                    'link': link,
                    'rating': 4.0 + (len(recommendations) * 0.2),  # Simulated rating
                    'image': 'https://via.placeholder.com/200x200'
                })
        
        # En az 2 öneri döndür
        if len(recommendations) < 2:
            recommendations.extend(self._get_fallback_recommendations(category))
            
        return recommendations[:5]  # Maksimum 5 öneri
    
    def _get_fallback_recommendations(self, category: str) -> List[Dict]:
        """
        Gemini AI başarısız olduğunda kullanılacak yedek öneriler.
        Artık boş liste döndürüyor ki frontend shopping API'sını kullansın.
        
        Args:
            category (str): Ürün kategorisi
            
        Returns:
            List[Dict]: Boş liste - frontend shopping API'sını kullanacak
        """
        logger.info(f"Gemini AI başarısız, frontend shopping API'sını kullanacak: {category}")
        return []  # Boş liste döndür ki frontend shopping API'sını kullansın
    
    def get_supported_countries(self) -> Dict[str, str]:
        """
        Desteklenen ülke listesini döndürür.
        
        Returns:
            Dict[str, str]: Ülke kod - isim eşleştirmesi
        """
        return self.shopping_api.get_supported_countries()
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Desteklenen dil listesini döndürür.
        
        Returns:
            Dict[str, str]: Dil kod - isim eşleştirmesi  
        """
        return ['tr', 'en']  # Supported languages


# Test fonksiyonu
if __name__ == "__main__":
    agent = EnhancedDatabaseCategoryAgent()
    
    # Test senaryoları
    test_cases = [
        ("kablosuz kulaklık", "tr"),
        ("gaming laptop", "en"),
        ("drone", "tr")
    ]
    
    for query, language in test_cases:
        print(f"\n=== Test: {query} ({language}) ===")
        
        # Kategori tespiti/oluşturma
        category, created = agent.get_or_create_category(query, language)
        print(f"Kategori: {category.name if category else 'None'}, Yeni: {created}")
        
        # Shopping önerileri
        if category:
            country = "TR" if language == "tr" else "US"
            recommendations = agent.get_shopping_recommendations(query, country, language)
            print(f"Ürün sayısı: {recommendations['total_results']}")
