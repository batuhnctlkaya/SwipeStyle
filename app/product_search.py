"""
Ürün Arama ve Filtreleme Modülü
===============================

Bu modül, kullanıcı tercihlerini Amazon arama parametrelerine çevirir
ve akıllı ürün filtreleme işlemlerini yönetir.

Özellikler:
- Kullanıcı tercihlerini arama sorgusuna çevirme
- Fiyat aralığı filtreleme
- Kategori bazlı arama
- Akıllı öneri sistemi
- Fiyat karşılaştırma

Kullanım:
    from app.product_search import ProductSearch
    
    search = ProductSearch()
    products = search.search_by_preferences(category, preferences, language)
"""

import re
from typing import Dict, List, Optional
from .amazon_api import AmazonAPI

class ProductSearch:
    """
    Ürün arama ve filtreleme işlemlerini yöneten ana sınıf.
    """
    
    def __init__(self):
        """
        ProductSearch sınıfını başlatır.
        """
        self.amazon_api = AmazonAPI()
        
        # Kategori-anahtar kelime eşleştirmeleri
        self.category_keywords = {
            'Headphones': ['kulaklık', 'headphone', 'earphone', 'bluetooth kulaklık'],
            'Phone': ['telefon', 'phone', 'smartphone', 'iphone', 'samsung'],
            'Laptop': ['laptop', 'bilgisayar', 'notebook', 'dizüstü'],
            'Mouse': ['mouse', 'fare', 'kablosuz mouse'],
            'Drill': ['matkap', 'drill', 'delici', 'akülü matkap'],
            'Chair': ['sandalye', 'chair', 'ofis sandalyesi', 'gaming chair'],
            'Car Mat': ['araç paspası', 'car mat', 'oto paspas'],
            'Klima': ['klima', 'air conditioner', 'ac', 'split klima'],
            'Bilgisayar': ['bilgisayar', 'computer', 'pc', 'masaüstü'],
            'Charger': ['şarj aleti', 'charger', 'sarj aleti', 'kablosuz şarj']
        }
        
        # Fiyat aralıkları (TRY)
        self.price_ranges = {
            'low': (0, 1000),
            'medium': (1000, 5000),
            'high': (5000, 15000),
            'premium': (15000, 100000)
        }
    
    def search_by_preferences(self, category: str, preferences: List[str], 
                            language: str = 'tr', max_results: int = 10) -> List[Dict]:
        """
        Kullanıcı tercihlerine göre Amazon'da ürün arama yapar.
        
        Args:
            category (str): Ürün kategorisi
            preferences (List[str]): Kullanıcı tercihleri
            language (str): Dil (tr/en)
            max_results (int): Maksimum sonuç sayısı
            
        Returns:
            List[Dict]: Bulunan ürünler
        """
        # Arama sorgusunu oluştur
        search_query = self._build_search_query(category, preferences, language)
        
        # Fiyat aralığını belirle
        min_price, max_price = self._get_price_range(preferences, language)
        
        # Amazon'da ara
        products = self.amazon_api.search_products(
            query=search_query,
            max_results=max_results,
            min_price=min_price,
            max_price=max_price,
            category=category
        )
        
        # Ürünleri filtrele ve sırala
        filtered_products = self._filter_and_sort_products(products, preferences, language)
        
        return filtered_products
    
    def _build_search_query(self, category: str, preferences: List[str], 
                           language: str) -> str:
        """
        Kullanıcı tercihlerinden arama sorgusu oluşturur.
        
        Args:
            category (str): Ürün kategorisi
            preferences (List[str]): Kullanıcı tercihleri
            language (str): Dil
            
        Returns:
            str: Arama sorgusu
        """
        # Kategori anahtar kelimelerini al
        category_keywords = self.category_keywords.get(category, [category.lower()])
        
        # Tercihlerden anahtar kelimeleri çıkar
        preference_keywords = []
        for preference in preferences:
            # Fiyat aralıklarını atla
            if self._is_price_range(preference):
                continue
            
            # Tercihten anahtar kelimeleri çıkar
            keywords = self._extract_keywords(preference, language)
            preference_keywords.extend(keywords)
        
        # Sorguyu birleştir
        query_parts = category_keywords[:1]  # Ana kategori
        query_parts.extend(preference_keywords[:3])  # İlk 3 tercih
        
        # Tekrarlanan kelimeleri kaldır
        unique_parts = list(dict.fromkeys(query_parts))
        
        search_query = ' '.join(unique_parts)
        
        print(f"🔍 Oluşturulan arama sorgusu: {search_query}")
        return search_query
    
    def _extract_keywords(self, text: str, language: str) -> List[str]:
        """
        Metinden anahtar kelimeleri çıkarır.
        
        Args:
            text (str): Metin
            language (str): Dil
            
        Returns:
            List[str]: Anahtar kelimeler
        """
        # Türkçe özel kelimeleri çıkar
        if language == 'tr':
            # Parantez içindeki açıklamaları kaldır
            text = re.sub(r'\([^)]*\)', '', text)
            
            # Yaygın kelimeleri kaldır
            stop_words = ['için', 've', 'veya', 'ile', 'bu', 'bir', 'da', 'de']
            words = text.lower().split()
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            
            return keywords[:3]  # İlk 3 anahtar kelime
        
        # İngilizce için basit kelime çıkarma
        else:
            text = re.sub(r'\([^)]*\)', '', text)
            words = text.lower().split()
            keywords = [word for word in words if len(word) > 2]
            return keywords[:3]
    
    def _is_price_range(self, text: str) -> bool:
        """
        Metnin fiyat aralığı olup olmadığını kontrol eder.
        
        Args:
            text (str): Kontrol edilecek metin
            
        Returns:
            bool: Fiyat aralığı ise True
        """
        price_patterns = [
            r'\d+-\d+₺',
            r'\d+k₺',
            r'\d+-\d+k₺',
            r'low|medium|high|premium'
        ]
        
        for pattern in price_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _get_price_range(self, preferences: List[str], language: str) -> tuple:
        """
        Kullanıcı tercihlerinden fiyat aralığını belirler.
        
        Args:
            preferences (List[str]): Kullanıcı tercihleri
            language (str): Dil
            
        Returns:
            tuple: (min_price, max_price)
        """
        min_price = None
        max_price = None
        
        for preference in preferences:
            # Türkçe fiyat formatları
            if language == 'tr':
                # 5.000-10.000₺ formatı
                match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)₺', preference)
                if match:
                    min_price = float(match.group(1).replace('.', ''))
                    max_price = float(match.group(2).replace('.', ''))
                    break
                
                # 25-40k₺ formatı
                match = re.search(r'(\d+)-(\d+)k₺', preference)
                if match:
                    min_price = float(match.group(1)) * 1000
                    max_price = float(match.group(2)) * 1000
                    break
                
                # Tek fiyat 3-6k₺
                match = re.search(r'(\d+)-(\d+)k₺', preference)
                if match:
                    min_price = float(match.group(1)) * 1000
                    max_price = float(match.group(2)) * 1000
                    break
            
            # İngilizce fiyat formatları
            else:
                # $100-$500 formatı
                match = re.search(r'\$(\d+)-?\$?(\d+)', preference)
                if match:
                    min_price = float(match.group(1))
                    max_price = float(match.group(2))
                    break
        
        return min_price, max_price
    
    def _filter_and_sort_products(self, products: List[Dict], 
                                 preferences: List[str], 
                                 language: str) -> List[Dict]:
        """
        Ürünleri filtreler ve tercihlere göre sıralar.
        
        Args:
            products (List[Dict]): Ürün listesi
            preferences (List[str]): Kullanıcı tercihleri
            language (str): Dil
            
        Returns:
            List[Dict]: Filtrelenmiş ve sıralanmış ürünler
        """
        if not products:
            return []
        
        # Her ürün için puan hesapla
        scored_products = []
        for product in products:
            score = self._calculate_product_score(product, preferences, language)
            product['score'] = score
            scored_products.append(product)
        
        # Puana göre sırala (yüksek puan önce)
        scored_products.sort(key=lambda x: x['score'], reverse=True)
        
        # Puanları kaldır (sadece sıralama için kullanıldı)
        for product in scored_products:
            product.pop('score', None)
        
        return scored_products
    
    def _calculate_product_score(self, product: Dict, preferences: List[str], 
                                language: str) -> float:
        """
        Ürün için uygunluk puanı hesaplar.
        
        Args:
            product (Dict): Ürün bilgileri
            preferences (List[str]): Kullanıcı tercihleri
            language (str): Dil
            
        Returns:
            float: Uygunluk puanı (0-100)
        """
        score = 0.0
        
        # Fiyat uygunluğu (30 puan)
        price_score = self._calculate_price_score(product, preferences, language)
        score += price_score * 0.3
        
        # Özellik uygunluğu (40 puan)
        feature_score = self._calculate_feature_score(product, preferences, language)
        score += feature_score * 0.4
        
        # Değerlendirme puanı (20 puan)
        rating_score = self._calculate_rating_score(product)
        score += rating_score * 0.2
        
        # Prime üyelik bonusu (10 puan)
        if product.get('prime', False):
            score += 10
        
        return min(score, 100)  # Maksimum 100 puan
    
    def _calculate_price_score(self, product: Dict, preferences: List[str], 
                              language: str) -> float:
        """
        Fiyat uygunluk puanını hesaplar.
        
        Args:
            product (Dict): Ürün bilgileri
            preferences (List[str]): Kullanıcı tercihleri
            language (str): Dil
            
        Returns:
            float: Fiyat puanı (0-100)
        """
        current_price = product.get('price', {}).get('current', 0)
        if current_price == 0:
            return 50  # Fiyat bilgisi yoksa orta puan
        
        # Kullanıcının bütçe aralığını bul
        min_price, max_price = self._get_price_range(preferences, language)
        
        if min_price is None or max_price is None:
            return 70  # Bütçe bilgisi yoksa yüksek puan
        
        # Fiyat aralığında mı kontrol et
        if min_price <= current_price <= max_price:
            return 100  # Mükemmel uyum
        elif current_price <= max_price * 1.2:
            return 80   # Biraz yüksek ama kabul edilebilir
        elif current_price <= max_price * 1.5:
            return 60   # Yüksek ama düşünülebilir
        else:
            return 20   # Çok yüksek
    
    def _calculate_feature_score(self, product: Dict, preferences: List[str], 
                                language: str) -> float:
        """
        Özellik uygunluk puanını hesaplar.
        
        Args:
            product (Dict): Ürün bilgileri
            preferences (List[str]): Kullanıcı tercihleri
            language (str): Dil
            
        Returns:
            float: Özellik puanı (0-100)
        """
        score = 50  # Başlangıç puanı
        
        product_title = product.get('title', '').lower()
        product_features = [f.lower() for f in product.get('features', [])]
        
        # Her tercih için kontrol et
        for preference in preferences:
            preference_lower = preference.lower()
            
            # Başlıkta geçiyor mu?
            if preference_lower in product_title:
                score += 10
            
            # Özelliklerde geçiyor mu?
            for feature in product_features:
                if preference_lower in feature:
                    score += 5
        
        return min(score, 100)
    
    def _calculate_rating_score(self, product: Dict) -> float:
        """
        Değerlendirme puanını hesaplar.
        
        Args:
            product (Dict): Ürün bilgileri
            
        Returns:
            float: Değerlendirme puanı (0-100)
        """
        rating = product.get('rating', 0)
        reviews_count = product.get('reviews_count', 0)
        
        # Yıldız puanı (0-5 -> 0-50)
        star_score = rating * 10
        
        # Yorum sayısı bonusu (0-50)
        review_bonus = min(reviews_count / 100, 50)
        
        return star_score + review_bonus 