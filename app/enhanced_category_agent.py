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
import requests
import time
import random
from urllib.parse import quote_plus, urljoin, urlparse
import google.generativeai as genai
from typing import Optional, Tuple, Dict, List
from app.models import db, Category, CategorySpec, UserSettings
import logging


# Try to import serpapi if available
try:
    from serpapi import Client
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False

# Try to import BeautifulSoup for free scraping
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

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
        
        # Simple translation cache to reduce API calls
        self.translation_cache = {}
        
        # Daily API usage tracking
        self.daily_api_calls = 0
        self.daily_limit = 50  # Free tier limit
        self.last_reset_date = None
        
        # Shopping API configuration
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        if not self.serpapi_key:
            logger.info("SERPAPI_KEY bulunamadı. Ücretsiz scraping modu kullanılacak.")
        
        # User agents for web scraping
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Türkçe kategori anahtar kelimeleri (genişletilmiş ve düzenlenmiş)
        self.turkish_keywords = {
            'phones': ['akıllı telefon', 'smartphone', 'cep telefonu', 'mobil telefon', 'telefon', 'iphone', 'android telefon'],
            'laptops': ['laptop', 'dizüstü bilgisayar', 'notebook', 'dizüstü', 'macbook', 'ultrabook', 'gaming laptop'],
            'headphones': ['kulaklık', 'kablosuz kulaklık', 'bluetooth kulaklık', 'kulak içi kulaklık', 'kulak üstü kulaklık', 'airpods', 'wireless kulaklık'],
            'tablets': ['tablet', 'ipad', 'android tablet', 'dokunmatik tablet'],
            'smartwatches': ['akıllı saat', 'smart watch', 'apple watch', 'samsung watch', 'fitness tracker', 'spor saati'],
            'cameras': ['kamera', 'fotoğraf makinesi', 'video kamera', 'dslr kamera', 'mirrorless kamera', 'dijital kamera'],
            'keyboards': ['klavye', 'mekanik klavye', 'gaming klavye', 'kablosuz klavye', 'oyuncu klavyesi'],
            'mice': ['mouse', 'fare', 'gaming mouse', 'kablosuz mouse', 'bluetooth mouse', 'oyuncu mouse'],
            'monitors': ['monitör', 'ekran', 'gaming monitör', '4k monitör', 'ultrawide monitör', 'bilgisayar ekranı'],
            'speakers': ['hoparlör', 'bluetooth hoparlör', 'kablosuz hoparlör', 'speaker', 'ses sistemi'],
            'printers': ['yazıcı', 'printer', 'lazer yazıcı', 'inkjet yazıcı'],
            'routers': ['modem', 'router', 'wifi router', 'kablosuz router', 'ağ cihazı'],
            'drones': ['drone', 'quadcopter', 'uav', 'drön', 'hava aracı'],
            'gaming': ['oyun konsolu', 'gaming konsol', 'playstation', 'xbox', 'nintendo', 'oyun'],
            'storage': ['harddisk', 'ssd', 'usb bellek', 'flash disk', 'harici disk', 'depolama']
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
    
    def _check_daily_limit(self) -> bool:
        """Günlük API limitini kontrol eder."""
        from datetime import date
        today = date.today()
        
        # Yeni gün başladıysa sayacı sıfırla
        if self.last_reset_date != today:
            self.daily_api_calls = 0
            self.last_reset_date = today
        
        return self.daily_api_calls < self.daily_limit
    
    def _increment_api_usage(self):
        """API kullanım sayacını artırır."""
        self.daily_api_calls += 1
        logger.debug(f"API kullanımı: {self.daily_api_calls}/{self.daily_limit}")
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Gemini AI kullanarak metin çevirisi yapar. Cache kullanır.
        
        Args:
            text (str): Çevrilecek metin
            source_lang (str): Kaynak dil kodu
            target_lang (str): Hedef dil kodu
            
        Returns:
            str: Çevrilmiş metin
        """
        # Cache key oluştur
        cache_key = f"{text}_{source_lang}_{target_lang}"
        
        # Cache'de var mı kontrol et
        if cache_key in self.translation_cache:
            logger.debug(f"Translation cache hit: {text[:50]}...")
            return self.translation_cache[cache_key]
        
        # Günlük limit kontrolü
        if not self._check_daily_limit():
            logger.warning(f"Günlük API limiti aşıldı ({self.daily_limit}). Orijinal metin döndürülüyor.")
            return text
        
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
            
            # Cache'e kaydet
            self.translation_cache[cache_key] = translation
            self._increment_api_usage()
            
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
        
        # Direkt isim eşleşmesi (daha akıllı eşleştirme)
        for category in all_categories:
            category_name_lower = category.name.lower()
            # Tam eşleşme kontrolü
            if query_lower == category_name_lower:
                return category
            # Kategori adı sorguyu içeriyorsa (ama tersi değil - bu false positive yaratır)
            if query_lower in category_name_lower and len(query_lower) > 3:
                # Özel kontrol: "phone" gibi kısa kelimeler "headphones" ile eşleşmesin
                if query_lower == "phone" and "headphone" in category_name_lower:
                    continue
                return category
        
        # Türkçe anahtar kelime eşleşmesi
        if language == "tr":
            # Kategori tipi ile veritabanındaki kategori adları arasında eşleştirme (daha kesin eşleşme)
            category_mapping = {
                'phones': ['smartphone', 'telefon', 'mobile'],  # More specific mappings
                'headphones': ['headphone', 'kulaklık', 'earphone', 'earbud'],
                'laptops': ['laptop', 'notebook', 'dizüstü'],
                'tablets': ['tablet', 'ipad'],
                'smartwatches': ['smartwatch', 'smart watch', 'akıllı saat'],
                'cameras': ['camera', 'kamera'],
                'keyboards': ['keyboard', 'klavye'],
                'mice': ['mouse', 'fare'],
                'monitors': ['monitor', 'monitör', 'ekran'],
                'speakers': ['speaker', 'hoparlör'],
                'printers': ['printer', 'yazıcı'],
                'routers': ['router', 'modem'],
                'drones': ['drone', 'drön'],
                'gaming': ['gaming', 'oyun'],
                'storage': ['storage', 'disk', 'depolama']
            }
            
            # Önce daha spesifik kategoriler için arama yap
            matched_categories = []
            for category_type, keywords in self.turkish_keywords.items():
                # Spesifik eşleşme skorunu hesapla
                for keyword in keywords:
                    if keyword in query_lower:
                        # Bu anahtar kelimeye uygun kategori var mı?
                        mapping_keywords = category_mapping.get(category_type, [category_type])
                        for category in all_categories:
                            category_name_lower = category.name.lower()
                            for mapping_keyword in mapping_keywords:
                                if mapping_keyword in category_name_lower:
                                    # Özel kontrol: telefon ile kulaklık karışmasın
                                    if category_type == 'phones' and ('headphone' in category_name_lower or 'kulaklık' in category_name_lower):
                                        continue  # Bu eşleşmeyi atla
                                    # Eşleşme skoru: daha uzun/spesifik kelimeler daha yüksek skor
                                    score = len(keyword) + (10 if query_lower == keyword else 0)
                                    matched_categories.append((category, score, keyword, category_type))
            
            # En yüksek skorlu kategoriyi döndür
            if matched_categories:
                matched_categories.sort(key=lambda x: x[1], reverse=True)
                logger.info(f"Turkish keyword match: '{matched_categories[0][2]}' (type: {matched_categories[0][3]}) -> {matched_categories[0][0].name}")
                return matched_categories[0][0]
        
        # İngilizce için benzer mantık
        elif language == "en":
            english_keywords = {
                'phones': ['smartphone', 'phone', 'mobile phone', 'iphone', 'android phone', 'cell phone'],
                'headphones': ['headphones', 'headphone', 'earphones', 'earbuds', 'airpods', 'wireless headphones', 'bluetooth headphones'],
                'laptops': ['laptop', 'notebook', 'macbook', 'computer laptop', 'gaming laptop'],
                'tablets': ['tablet', 'ipad', 'android tablet'],
                'smartwatches': ['smartwatch', 'smart watch', 'apple watch', 'fitness tracker'],
                'cameras': ['camera', 'dslr', 'mirrorless', 'digital camera'],
                'keyboards': ['keyboard', 'mechanical keyboard', 'gaming keyboard'],
                'mice': ['mouse', 'gaming mouse', 'computer mouse'],
                'monitors': ['monitor', 'display', 'screen', 'gaming monitor'],
                'speakers': ['speaker', 'bluetooth speaker', 'wireless speaker'],
                'printers': ['printer', 'laser printer', 'inkjet printer'],
                'routers': ['router', 'wifi router', 'wireless router'],
                'drones': ['drone', 'quadcopter', 'uav'],
                'gaming': ['gaming console', 'playstation', 'xbox', 'nintendo'],
                'storage': ['hard drive', 'ssd', 'external drive', 'usb drive']
            }
            
            # Kategori tipi ile veritabanındaki kategori adları arasında eşleştirme (daha kesin eşleşme)
            category_mapping = {
                'phones': ['smartphone', 'mobile phone', 'mobile'],  # Removed 'phone' to avoid confusion with 'headphone'
                'headphones': ['headphone', 'earphone', 'earbud'],
                'laptops': ['laptop', 'notebook'],
                'tablets': ['tablet', 'ipad'],
                'smartwatches': ['smartwatch', 'smart watch'],
                'cameras': ['camera'],
                'keyboards': ['keyboard'],
                'mice': ['mouse'],
                'monitors': ['monitor', 'display', 'screen'],
                'speakers': ['speaker'],
                'printers': ['printer'],
                'routers': ['router', 'modem'],
                'drones': ['drone'],
                'gaming': ['gaming', 'console'],
                'storage': ['storage', 'drive']
            }
            
            # Önce daha spesifik kategoriler için arama yap
            matched_categories = []
            for category_type, keywords in english_keywords.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        # Bu anahtar kelimeye uygun kategori var mı?
                        mapping_keywords = category_mapping.get(category_type, [category_type])
                        for category in all_categories:
                            category_name_lower = category.name.lower()
                            for mapping_keyword in mapping_keywords:
                                # Daha kesin eşleşme: mapping_keyword'ün tam olarak category name'de olması
                                if mapping_keyword in category_name_lower:
                                    # Ayrıca 'phone' kelimesi için özel kontrol: 'headphone' ile karışmasın
                                    if category_type == 'phones' and 'headphone' in category_name_lower:
                                        continue  # Bu eşleşmeyi atla
                                    # Eşleşme skoru: daha uzun/spesifik kelimeler daha yüksek skor
                                    score = len(keyword) + (10 if query_lower == keyword else 0)
                                    matched_categories.append((category, score, keyword, category_type))
            
            # En yüksek skorlu kategoriyi döndür
            if matched_categories:
                matched_categories.sort(key=lambda x: x[1], reverse=True)
                logger.info(f"English keyword match: '{matched_categories[0][2]}' (type: {matched_categories[0][3]}) -> {matched_categories[0][0].name}")
                return matched_categories[0][0]
        
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
        # Günlük limit kontrolü
        if not self._check_daily_limit():
            logger.warning(f"Günlük API limiti aşıldı ({self.daily_limit}). Kategori oluşturulamıyor.")
            return None
            
        if not self.model:
            logger.error("Gemini AI model bulunamadı, kategori oluşturulamıyor")
            return None
        
        try:
            # Rate limiting
            self._wait_for_rate_limit()
            
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
            
            self._increment_api_usage()
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
            products = self.search_products(query, country, language, max_results=8)
            
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
            step = data.get('step', 1)
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
            
            # Category specifications (start from step 1)
            spec_step = step - 1  # Convert to 0-based index
            
            if spec_step < len(specs) and spec_step >= 0:
                # Sonraki soruyu döndür
                spec = specs[spec_step]
                
                # Always use Yes/No options for specs
                options = ['Evet', 'Hayır'] if language == 'tr' else ['Yes', 'No']
                
                return {
                    'question': spec.get('question', ''),
                    'options': options,
                    'emoji': spec.get('emoji', '�'),
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
                    recommendations = self._generate_gemini_recommendations(
                        category_name, selected_specs, language
                    )
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
    
    def _get_budget_options(self, country: str, language: str) -> List[str]:
        """
        Ülke ve dile göre bütçe seçeneklerini döndürür.
        
        Args:
            country (str): Ülke kodu
            language (str): Dil kodu
            
        Returns:
            List[str]: Bütçe seçenekleri
        """
        budget_ranges = {
            'TR': {
                'tr': ['0-500 ₺', '500-1.000 ₺', '1.000-2.500 ₺', '2.500-5.000 ₺', '5.000+ ₺'],
                'en': ['0-500 ₺', '500-1,000 ₺', '1,000-2,500 ₺', '2,500-5,000 ₺', '5,000+ ₺']
            },
            'US': {
                'tr': ['$0-100', '$100-250', '$250-500', '$500-1.000', '$1.000+'],
                'en': ['$0-100', '$100-250', '$250-500', '$500-1,000', '$1,000+']
            },
            'GB': {
                'tr': ['£0-75', '£75-200', '£200-400', '£400-750', '£750+'],
                'en': ['£0-75', '£75-200', '£200-400', '£400-750', '£750+']
            },
            'DE': {
                'tr': ['€0-85', '€85-215', '€215-430', '€430-850', '€850+'],
                'en': ['€0-85', '€85-215', '€215-430', '€430-850', '€850+']
            },
            'FR': {
                'tr': ['€0-85', '€85-215', '€215-430', '€430-850', '€850+'],
                'en': ['€0-85', '€85-215', '€215-430', '€430-850', '€850+']
            }
        }
        
        return budget_ranges.get(country, budget_ranges['US']).get(language, budget_ranges['US']['en'])
    
    def _generate_gemini_recommendations_with_budget(self, category: str, selected_specs: List[str], 
                                                   budget: str, language: str = "tr", session_id: str = None) -> List[Dict]:
        """
        Bütçe dahil Gemini AI kullanarak ürün önerileri üretir.
        
        Args:
            category (str): Ürün kategorisi
            selected_specs (List[str]): Kullanıcının seçtiği özellikler
            budget (str): Kullanıcının bütçesi
            language (str): Dil kodu
            session_id (str): Oturum ID'si
            
        Returns:
            List[Dict]: Ürün önerileri listesi
        """
        try:
            if not self.model:
                logger.error("Gemini model bulunamadı")
                return self._get_fallback_recommendations(category)
            
            # Rate limiting koruması
            self._wait_for_rate_limit()
            
            # Get user's country for currency
            user_settings = self.get_user_settings(session_id) if session_id else {}
            country = user_settings.get('country', 'TR')
            
            prompt = self._build_budget_recommendation_prompt(category, selected_specs, budget, language, country)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                recommendations = self._parse_gemini_response(response.text, category)
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
    
    def _build_budget_recommendation_prompt(self, category: str, selected_specs: List[str], 
                                         budget: str, language: str, country: str) -> str:
        """
        Bütçe dahil Gemini AI için ürün önerisi prompt'u oluşturur.
        
        Args:
            category (str): Ürün kategorisi
            selected_specs (List[str]): Seçilen özellikler
            budget (str): Bütçe aralığı
            language (str): Dil kodu
            country (str): Ülke kodu
            
        Returns:
            str: Hazırlanmış prompt
        """
        specs_str = ', '.join(selected_specs) if selected_specs else "temel özellikler"
        
        if language == 'tr':
            prompt = (
                f"'{category}' kategorisinde, '{budget}' bütçe aralığında, şu özelliklere sahip ürünler öner: {specs_str}. "
                f"Türk pazarında satılan gerçek ürünleri öner. "
                "Her ürün için isim, fiyat ve kısa açıklama ver. "
                "5 ürün öner. Bütçe sınırını kesinlikle aşma. "
                "Sadece aşağıdaki örnekteki gibi kısa bir liste olarak dön.\n\n"
                "Örnek çıktı:\n"
                "Sony WH-1000XM4 - 1.200 ₺ - Kablosuz, noise cancelling\n"
                "Apple AirPods Pro - 2.000 ₺ - True wireless, ANC\n\n"
                "Lütfen sadece bu formatta dön: Ürün Adı - Fiyat - Kısa Açıklama."
            )
        else:
            currency_symbols = {'US': '$', 'GB': '£', 'DE': '€', 'FR': '€', 'TR': '₺'}
            currency = currency_symbols.get(country, '$')
            
            prompt = (
                f"Recommend products in the '{category}' category within the '{budget}' budget range "
                f"with these features: {specs_str}. "
                "For each product, provide name, price, and brief description. "
                "Recommend 5 products. Do not exceed the budget limit. "
                "Return as a simple list like the example below.\n\n"
                "Example output:\n"
                f"Sony WH-1000XM4 - {currency}350 - Wireless, noise cancelling\n"
                f"Apple AirPods Pro - {currency}250 - True wireless, ANC\n\n"
                "Please return only in this format: Product Name - Price - Brief Description."
            )
        
        return prompt
    
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
                "Sony WH 1000XM4 - FIYAT - Kablosuz, noise cancelling\n"
                "Apple AirPods Pro - FIYAT - True wireless, ANC\n\n"
                "Lütfen sadece bu formatta dön: Ürün Adı - Fiyat - Kısa Açıklama."
            )
        else:
            prompt = (
                f"Recommend products in the '{category}' category with these features: {specs_str}. "
                "For each product, provide name, estimated price (in USD), and brief description. "
                "Recommend 5 products. Return as a simple list like the example below.\n\n"
                "Example output:\n"
                "Sony WH 1000XM4 - $350 - Wireless, noise cancelling\n"
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
        return {
            "TR": "Türkiye",
            "US": "United States", 
            "GB": "United Kingdom",
            "DE": "Germany",
            "FR": "France"
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Desteklenen dil listesini döndürür.
        
        Returns:
            Dict[str, str]: Dil kod - isim eşleştirmesi  
        """
        return {
            "tr": "Türkçe",
            "en": "English"
        }
    
    def search_products(self, query: str, country: str = "TR", language: str = "tr", max_results: int = 10) -> List[Dict]:
        """
        Google Shopping'te ürün araması yapar.
        
        Args:
            query (str): Arama sorgusu (örn: "wireless headphones")
            country (str): Ülke kodu ("TR", "US", "GB", vb.)
            language (str): Dil kodu ("tr", "en")
            max_results (int): Maksimum sonuç sayısı
            
        Returns:
            List[Dict]: Ürün listesi
        """
        # Try SerpApi first if available
        if self.serpapi_key and SERPAPI_AVAILABLE:
            return self._search_with_serpapi(query, country, language, max_results)
        
        # Fallback to free scraping
        elif BS4_AVAILABLE:
            return self._search_with_scraping(query, country, language, max_results)
        
        # Ultimate fallback to enhanced mock data
        else:
            return self._get_enhanced_mock_products(query, country, language, max_results)
    
    def _search_with_serpapi(self, query: str, country: str, language: str, max_results: int) -> List[Dict]:
        """
        SerpApi kullanarak Google Shopping araması yapar.
        """
        try:
            # Country and language mapping
            country_map = {
                "TR": {"google_domain": "google.com.tr", "gl": "tr", "hl": "tr"},
                "US": {"google_domain": "google.com", "gl": "us", "hl": "en"},
                "GB": {"google_domain": "google.co.uk", "gl": "uk", "hl": "en"},
                "DE": {"google_domain": "google.de", "gl": "de", "hl": "de"},
                "FR": {"google_domain": "google.fr", "gl": "fr", "hl": "fr"}
            }
            
            country_config = country_map.get(country, country_map["US"])
            
            # SerpApi parametreleri
            params = {
                "engine": "google_shopping",
                "q": query,
                "google_domain": country_config["google_domain"],
                "gl": country_config["gl"],
                "hl": language if language in ["tr", "en", "de", "fr"] else "en",
                "api_key": self.serpapi_key,
                "num": min(max_results, 20)  # SerpApi limit
            }
            
            # API çağrısı yap
            client = Client(api_key=self.serpapi_key)
            results = client.search(params)
            
            # Sonuçları işle
            products = []
            shopping_results = results.get("shopping_results", [])
            
            for result in shopping_results[:max_results]:
                product = {
                    "title": result.get("title", ""),
                    "price": result.get("price", ""),
                    "source": result.get("source", ""),
                    "link": result.get("link", ""),
                    "image": result.get("thumbnail", ""),
                    "rating": result.get("rating", None),
                    "reviews": result.get("reviews", None),
                    "position": result.get("position", 0)
                }
                
                # Fiyat formatını temizle
                if product["price"]:
                    product["price"] = self._clean_price(product["price"], country)
                
                products.append(product)
            
            logger.info(f"SerpApi'den {len(products)} ürün bulundu: {query}")
            return products
            
        except Exception as e:
            logger.error(f"SerpApi hatası: {str(e)}")
            return self._get_enhanced_mock_products(query, country, language, max_results)
    
    def _search_with_scraping(self, query: str, country: str, language: str, max_results: int) -> List[Dict]:
        """
        Ücretsiz web scraping ile ürün araması yapar.
        """
        try:
            # Different search engines for different countries
            search_urls = {
                "TR": f"https://www.google.com.tr/search?q={quote_plus(query)}&tbm=shop&hl=tr&gl=tr",
                "US": f"https://www.google.com/search?q={quote_plus(query)}&tbm=shop&hl=en&gl=us",
                "GB": f"https://www.google.co.uk/search?q={quote_plus(query)}&tbm=shop&hl=en&gl=uk",
                "DE": f"https://www.google.de/search?q={quote_plus(query)}&tbm=shop&hl=de&gl=de",
                "FR": f"https://www.google.fr/search?q={quote_plus(query)}&tbm=shop&hl=fr&gl=fr"
            }
            
            url = search_urls.get(country, search_urls["US"])
            
            # Request headers
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': f'{language},en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse results with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                products = self._parse_google_shopping_results(soup, country, max_results)
                
                if products:
                    logger.info(f"Web scraping'den {len(products)} ürün bulundu: {query}")
                    return products
            
            # If scraping fails, return enhanced mock data
            logger.warning(f"Web scraping başarısız ({response.status_code}), mock data döndürülüyor")
            return self._get_enhanced_mock_products(query, country, language, max_results)
            
        except Exception as e:
            logger.error(f"Web scraping hatası: {str(e)}")
            return self._get_enhanced_mock_products(query, country, language, max_results)
    
    def _parse_google_shopping_results(self, soup, country: str, max_results: int) -> List[Dict]:
        """
        Google Shopping HTML sonuçlarını ayrıştırır.
        """
        products = []
        
        # Try to find product containers (Google changes these frequently)
        selectors = [
            '.sh-dgr__content',  # Common Google Shopping selector
            '.sh-dlr__list-result',
            '.sh-pr__product-results-grid',
            '.sh-np__click-target',
            '[data-sh-product-id]'
        ]
        
        product_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements[:max_results]
                break
        
        currency_map = {
            "TR": "₺",
            "US": "$", 
            "GB": "£",
            "DE": "€",
            "FR": "€"
        }
        
        default_currency = currency_map.get(country, "$")
        
        for i, element in enumerate(product_elements[:max_results]):
            try:
                # Extract title
                title_elem = element.find(['h3', 'h4', '[role="heading"]']) or element.find(string=True)
                title = title_elem.get_text(strip=True) if hasattr(title_elem, 'get_text') else str(title_elem)
                
                # Extract price
                price_elem = element.find(string=re.compile(r'[\$£€₺]\d+|TL|\d+,\d+'))
                price = price_elem.strip() if price_elem else f"{default_currency}99"
                
                # Extract source/store
                link_elem = element.find('a')
                source = "shopping-site.com"
                link = "#"
                
                if link_elem and link_elem.get('href'):
                    link = link_elem.get('href')
                    # Try to extract domain as source
                    if 'url?q=' in link:
                        real_url = link.split('url?q=')[1].split('&')[0]
                        try:
                            from urllib.parse import urlparse
                            source = urlparse(real_url).netloc
                        except:
                            pass
                
                # Extract image
                img_elem = element.find('img')
                image = img_elem.get('src', 'https://via.placeholder.com/200x200') if img_elem else 'https://via.placeholder.com/200x200'
                
                product = {
                    "title": title or f"Product {i+1}",
                    "price": self._clean_price(price, country),
                    "source": source,
                    "link": link,
                    "image": image,
                    "rating": round(4.0 + random.random(), 1),
                    "reviews": random.randint(50, 1500),
                    "position": i + 1
                }
                
                products.append(product)
                
            except Exception as e:
                logger.debug(f"Ürün ayrıştırma hatası: {e}")
                continue
        
        return products
    
    def _clean_price(self, price_str: str, country: str) -> str:
        """
        Fiyat string'ini temizler ve ülke formatına göre düzenler.
        """
        if not price_str:
            return ""
        
        # Genel temizlik
        price = price_str.strip()
        
        # Ülke bazlı formatlar
        if country == "TR":
            if "₺" not in price and any(char.isdigit() for char in price):
                price = f"₺{price}"
        elif country in ["US"]:
            if "$" not in price and any(char.isdigit() for char in price):
                price = f"${price}"
        elif country == "GB":
            if "£" not in price and any(char.isdigit() for char in price):
                price = f"£{price}"
        
        return price
    
    def _get_enhanced_mock_products(self, query: str, country: str = "TR", language: str = "tr", max_results: int = 10) -> List[Dict]:
        """
        Geliştirilmiş mock ürünler döndürür - daha gerçekçi veriler.
        """
        currency_map = {
            "TR": "₺",
            "US": "$", 
            "GB": "£",
            "DE": "€",
            "FR": "€"
        }
        
        currency = currency_map.get(country, "$")
        
        # Realistic product templates based on query
        product_templates = {
            # Electronics
            "headphone": ["Sony WH-1000XM5", "Bose QuietComfort 45", "Apple AirPods Pro", "Sennheiser HD 450BT", "JBL Tune 750BTNC"],
            "laptop": ["Apple MacBook Air M2", "Dell XPS 13", "HP Spectre x360", "Lenovo ThinkPad X1", "ASUS ZenBook 14"],
            "phone": ["iPhone 15 Pro", "Samsung Galaxy S24", "Google Pixel 8", "OnePlus 12", "Xiaomi 14 Pro"],
            "tablet": ["iPad Air", "Samsung Galaxy Tab S9", "Microsoft Surface Pro", "Lenovo Tab P12", "Huawei MatePad Pro"],
            "watch": ["Apple Watch Series 9", "Samsung Galaxy Watch6", "Garmin Forerunner 265", "Fitbit Sense 2", "Huawei Watch GT 4"]
        }
        
        # Find matching template
        query_lower = query.lower()
        template_products = None
        
        for category, products in product_templates.items():
            if category in query_lower:
                template_products = products
                break
        
        # Fallback to generic products
        if not template_products:
            template_products = [f"Premium {query.title()}", f"Professional {query.title()}", f"Budget {query.title()}", f"Advanced {query.title()}", f"Standard {query.title()}"]
        
        # Price ranges by country
        price_ranges = {
            "TR": [299, 599, 999, 1499, 2499],
            "US": [99, 199, 299, 499, 799],
            "GB": [89, 169, 249, 399, 649],
            "DE": [89, 169, 249, 399, 649],
            "FR": [89, 169, 249, 399, 649]
        }
        
        prices = price_ranges.get(country, price_ranges["US"])
        
        # Store names by country
        stores = {
            "TR": ["teknosa.com", "hepsiburada.com", "trendyol.com", "n11.com", "gittigidiyor.com"],
            "US": ["amazon.com", "bestbuy.com", "newegg.com", "target.com", "walmart.com"],
            "GB": ["amazon.co.uk", "currys.co.uk", "argos.co.uk", "very.co.uk", "johnlewis.com"],
            "DE": ["amazon.de", "mediamarkt.de", "saturn.de", "otto.de", "alternate.de"],
            "FR": ["amazon.fr", "fnac.com", "cdiscount.com", "darty.com", "boulanger.com"]
        }
        
        store_list = stores.get(country, stores["US"])
        
        mock_products = []
        
        # Get category images once for all products
        try:
            category_images = self.get_category_images(query, max_results)
            logger.info(f"Retrieved {len(category_images)} images for category: {query}")
        except Exception as e:
            logger.error(f"Error getting category images: {e}")
            category_images = []
        
        for i in range(min(max_results, len(template_products))):
            product_name = template_products[i]
            price = f"{currency}{prices[i % len(prices)]}"
            store = store_list[i % len(store_list)]
            
            # Create realistic search link
            search_query = quote_plus(product_name)
            if country == "TR":
                link = f"https://www.akakce.com/arama/?q={search_query}"
            else:
                link = f"https://www.google.com/search?tbm=shop&q={search_query}"
            
            # Use category image or fallback to placeholder
            if category_images and i < len(category_images):
                product_image = category_images[i]
            else:
                product_image = f"https://via.placeholder.com/200x200?text={quote_plus(product_name[:20])}"
            
            product = {
                "title": product_name,
                "price": price,
                "source": store,
                "link": link,
                "image": product_image,
                "rating": round(3.8 + random.random() * 1.2, 1),  # 3.8-5.0 range
                "reviews": random.randint(50, 2500),
                "position": i + 1
            }
            
            mock_products.append(product)
        
        logger.info(f"Enhanced mock ürünler döndürülüyor: {query} ({country}) - {len(mock_products)} ürün")
        return mock_products
    
    def get_category_images(self, category: str, max_images: int = 3) -> List[str]:
        """
        Kategori için resim URL'lerini getirir.
        
        Args:
            category (str): Kategori adı
            max_images (int): Maximum resim sayısı
            
        Returns:
            List[str]: Resim URL listesi
        """
        try:
            # Google Images search için search terimi oluştur
            search_term = f"{category} product images"
            
            # SerpApi ile Google Images araması
            if self.serpapi_key:
                params = {
                    "engine": "google_images",
                    "q": search_term,
                    "api_key": self.serpapi_key,
                    "num": max_images,
                    "safe": "active",
                    "image_type": "photo"
                }
                
                response = requests.get("https://serpapi.com/search", params=params)
                if response.status_code == 200:
                    data = response.json()
                    images = []
                    for result in data.get("images_results", [])[:max_images]:
                        if "original" in result:
                            images.append(result["original"])
                    return images
            
            # Fallback: Category-specific image URLs from Unsplash
            category_images = {
                # Electronics
                "electronics": [
                    "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400",
                    "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=400",
                    "https://images.unsplash.com/photo-1555774698-0b77e0d5fac6?w=400"
                ],
                "headphones": [
                    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                    "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400",
                    "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400"
                ],
                "headphone": [
                    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                    "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400",
                    "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400"
                ],
                "laptop": [
                    "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
                    "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
                    "https://images.unsplash.com/photo-1588702547919-26089e690ecc?w=400"
                ],
                "phone": [
                    "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
                    "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400",
                    "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400"
                ],
                "smartphone": [
                    "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
                    "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400",
                    "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400"
                ],
                "tablet": [
                    "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
                    "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400",
                    "https://images.unsplash.com/photo-1585790050230-5dd28404ccb9?w=400"
                ],
                "watch": [
                    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
                    "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400",
                    "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400"
                ],
                "smartwatch": [
                    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
                    "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400",
                    "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400"
                ]
            }
            
            # Kategori için özel resimler varsa kullan
            category_lower = category.lower()
            for key, images in category_images.items():
                if key.lower() in category_lower or category_lower in key.lower():
                    return images[:max_images]
            
            # Genel fallback resimler
            return [
                "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",
                "https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?w=400",
                "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"
            ][:max_images]
            
        except Exception as e:
            logger.error(f"Error fetching category images: {e}")
            return [
                "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",
                "https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?w=400",
                "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"
            ][:max_images]


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
