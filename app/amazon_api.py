"""
Amazon API Entegrasyon Modülü
============================

Bu modül, Rainforest API kullanarak Amazon'dan ürün bilgilerini çeker.
Mevcut SwipeStyle sistemini Amazon ürünleriyle entegre eder.

Özellikler:
- Amazon ürün arama
- Ürün detayları çekme
- Fiyat ve stok bilgisi
- Kullanıcı yorumları
- Fiyat karşılaştırma

Gereksinimler:
- Rainforest API anahtarı (RAINFOREST_API_KEY)
- requests kütüphanesi

Kullanım:
    from app.amazon_api import AmazonAPI
    
    api = AmazonAPI()
    products = api.search_products("laptop", max_results=10)
    product_details = api.get_product_details("B08N5WRWNW")
"""

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class AmazonAPI:
    """
    Amazon API entegrasyonu için ana sınıf.
    Rainforest API kullanarak Amazon'dan ürün bilgilerini çeker.
    """
    
    def __init__(self):
        """
        Amazon API sınıfını başlatır.
        API anahtarını environment variable'dan alır.
        """
        self.api_key = os.getenv('RAINFOREST_API_KEY')
        if not self.api_key:
            print("⚠️  RAINFOREST_API_KEY environment variable'ı bulunamadı!")
            print("   Rainforest API'den ücretsiz anahtar alabilirsiniz: https://www.rainforestapi.com/")
        
        self.base_url = "https://api.rainforestapi.com/request"
        self.country = "tr"  # Türkiye için
        self.currency = "TRY"
    
    def search_products(self, query: str, max_results: int = 10, 
                       min_price: Optional[float] = None, 
                       max_price: Optional[float] = None,
                       category: Optional[str] = None) -> List[Dict]:
        """
        Amazon'da ürün arama yapar.
        
        Args:
            query (str): Arama sorgusu
            max_results (int): Maksimum sonuç sayısı (varsayılan: 10)
            min_price (float): Minimum fiyat filtresi
            max_price (float): Maksimum fiyat filtresi
            category (str): Kategori filtresi
            
        Returns:
            List[Dict]: Ürün listesi
        """
        if not self.api_key:
            return self._get_mock_products(query, max_results)
        
        try:
            params = {
                'api_key': self.api_key,
                'type': 'search',
                'amazon_domain': 'amazon.com.tr',
                'search_term': query,
                'max_page': 1
            }
            
            if min_price:
                params['min_price'] = int(min_price)
            if max_price:
                params['max_price'] = int(max_price)
            
            print(f"🔍 Amazon'da aranıyor: {query}")
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('search_results', [])
                
                # Ürünleri formatla
                formatted_products = []
                for product in products[:max_results]:
                    formatted_product = self._format_product(product)
                    formatted_products.append(formatted_product)
                
                print(f"✅ {len(formatted_products)} ürün bulundu")
                return formatted_products
            else:
                print(f"❌ API hatası: {response.status_code}")
                return self._get_mock_products(query, max_results)
                
        except Exception as e:
            print(f"❌ Amazon API hatası: {e}")
            return self._get_mock_products(query, max_results)
    
    def get_product_details(self, asin: str) -> Optional[Dict]:
        """
        Belirli bir ürünün detaylarını çeker.
        
        Args:
            asin (str): Amazon ASIN kodu
            
        Returns:
            Dict: Ürün detayları
        """
        if not self.api_key:
            return self._get_mock_product_details(asin)
        
        try:
            params = {
                'api_key': self.api_key,
                'type': 'product',
                'amazon_domain': 'amazon.com.tr',
                'asin': asin
            }
            
            print(f"📦 Ürün detayları çekiliyor: {asin}")
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                product = data.get('product', {})
                return self._format_product_details(product)
            else:
                print(f"❌ Ürün detay hatası: {response.status_code}")
                return self._get_mock_product_details(asin)
                
        except Exception as e:
            print(f"❌ Ürün detay API hatası: {e}")
            return self._get_mock_product_details(asin)
    
    def get_price_history(self, asin: str) -> List[Dict]:
        """
        Ürünün fiyat geçmişini çeker.
        
        Args:
            asin (str): Amazon ASIN kodu
            
        Returns:
            List[Dict]: Fiyat geçmişi
        """
        # Rainforest API'nin fiyat geçmişi özelliği yok
        # Bu özellik için ayrı bir servis gerekebilir
        return []
    
    def _format_product(self, product: Dict) -> Dict:
        """
        Amazon API'den gelen ürün verisini formatlar.
        
        Args:
            product (Dict): Ham ürün verisi
            
        Returns:
            Dict: Formatlanmış ürün verisi
        """
        try:
            return {
                'asin': product.get('asin', ''),
                'title': product.get('title', ''),
                'price': {
                    'current': product.get('price', {}).get('value', 0),
                    'currency': product.get('price', {}).get('currency', 'TRY'),
                    'original': product.get('price', {}).get('original_value', 0)
                },
                'rating': product.get('rating', 0),
                'reviews_count': product.get('ratings_total', 0),
                'image': product.get('image', ''),
                'url': product.get('link', ''),
                'availability': product.get('availability', ''),
                'prime': product.get('is_prime', False),
                'sponsored': product.get('sponsored', False),
                'features': product.get('features', []),
                'categories': product.get('categories', [])
            }
        except Exception as e:
            print(f"❌ Ürün formatlama hatası: {e}")
            return {}
    
    def _format_product_details(self, product: Dict) -> Dict:
        """
        Ürün detaylarını formatlar.
        
        Args:
            product (Dict): Ham ürün detay verisi
            
        Returns:
            Dict: Formatlanmış ürün detayları
        """
        try:
            return {
                'asin': product.get('asin', ''),
                'title': product.get('title', ''),
                'description': product.get('description', ''),
                'price': {
                    'current': product.get('price', {}).get('value', 0),
                    'currency': product.get('price', {}).get('currency', 'TRY'),
                    'original': product.get('price', {}).get('original_value', 0)
                },
                'rating': product.get('rating', 0),
                'reviews_count': product.get('ratings_total', 0),
                'images': product.get('images', []),
                'url': product.get('link', ''),
                'availability': product.get('availability', ''),
                'prime': product.get('is_prime', False),
                'features': product.get('features', []),
                'specifications': product.get('specifications', []),
                'reviews': product.get('reviews', []),
                'variants': product.get('variants', []),
                'categories': product.get('categories', [])
            }
        except Exception as e:
            print(f"❌ Ürün detay formatlama hatası: {e}")
            return {}
    
    def _get_mock_products(self, query: str, max_results: int) -> List[Dict]:
        """
        API anahtarı yoksa mock ürünler döndürür.
        
        Args:
            query (str): Arama sorgusu
            max_results (int): Maksimum sonuç sayısı
            
        Returns:
            List[Dict]: Mock ürün listesi
        """
        print(f"🔄 Mock ürünler oluşturuluyor: {query}")
        
        # Kategori bazlı gerçekçi ürün adları
        product_names = {
            'mouse': [
                'Logitech G203 Lightsync Gaming Mouse',
                'Razer DeathAdder V2 Gaming Mouse',
                'SteelSeries Rival 3 Gaming Mouse',
                'Corsair M65 RGB Elite Gaming Mouse',
                'HyperX Pulsefire Haste Gaming Mouse'
            ],
            'klavye': [
                'Logitech G Pro X Mechanical Gaming Keyboard',
                'Razer BlackWidow V3 Pro Wireless Keyboard',
                'SteelSeries Apex Pro TKL Gaming Keyboard',
                'Corsair K100 RGB Mechanical Keyboard',
                'HyperX Alloy Origins Core Gaming Keyboard'
            ],
                         'kulaklık': [
                 'Anker Soundcore Liberty 4 NC',
                 'Sony WF-C700N',
                 'Samsung Galaxy Buds FE',
                 'Huawei FreeBuds 5i',
                 'JBL Live Pro 2 TWS'
             ],
            'laptop': [
                'ASUS ROG Strix G15 Gaming Laptop',
                'MSI GE76 Raider Gaming Laptop',
                'Lenovo Legion 5 Pro Gaming Laptop',
                'Acer Predator Helios 300 Gaming Laptop',
                'HP Omen 15 Gaming Laptop'
            ],
            'telefon': [
                'iPhone 15 Pro Max 256GB',
                'Samsung Galaxy S24 Ultra 256GB',
                'Google Pixel 8 Pro 256GB',
                'OnePlus 12 256GB',
                'Xiaomi 14 Pro 256GB'
            ]
        }
        
        # Query'ye göre ürün adlarını seç
        query_lower = query.lower()
        names = product_names.get(query_lower, [f'Premium {query.title()} {i+1}' for i in range(5)])
        
        # Gerçekçi fiyatlar - 1.5k-3k aralığında daha fazla ürün
        base_prices = {
            'mouse': [150, 250, 350, 450, 550],
            'klavye': [800, 1200, 1800, 2500, 3500],
            'kulaklık': [1600, 2200, 2800, 3500, 4200],  # 1.5k-3k aralığında
            'laptop': [15000, 25000, 35000, 45000, 55000],
            'telefon': [25000, 35000, 45000, 55000, 65000]
        }
        
        prices = base_prices.get(query_lower, [100 + (i * 50) for i in range(5)])
        
        mock_products = []
        for i in range(min(max_results, 5)):
            current_price = prices[i] if i < len(prices) else 100 + (i * 50)
            original_price = int(current_price * 1.3)  # %30 indirim
            
            # Fiyat filtresi uygula (1.5k-3k aralığı için)
            if query_lower == 'kulaklık' and (current_price < 1500 or current_price > 3000):
                continue
            
            mock_products.append({
                'asin': f'B0{query_lower[:3].upper()}{i:06d}',
                'title': names[i] if i < len(names) else f'Premium {query.title()} {i+1}',
                'price': {
                    'current': current_price,
                    'currency': 'TRY',
                    'original': original_price
                },
                'rating': 4.2 + (i * 0.1),
                'reviews_count': 150 + (i * 75),
                'image': self._get_product_image(query_lower, i),
                                 'url': self._get_search_url(query_lower, i),
                'availability': 'Stokta',
                'prime': True,
                'sponsored': i == 0,  # İlk ürün reklam
                'features': [
                    'Yüksek performans',
                    'Dayanıklı tasarım',
                    'Kolay kullanım'
                ],
                'categories': ['Elektronik', query.title()]
            })
        
        return mock_products
    
    def _get_product_image(self, category: str, index: int) -> str:
         """
         Kategori bazlı gerçekçi ürün görselleri döndürür.
         
         Args:
             category (str): Ürün kategorisi
             index (int): Ürün indeksi
             
         Returns:
             str: Ürün görseli URL'i
         """
         # Kategori bazlı görsel URL'leri
         product_images = {
             'mouse': [
                 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop&sat=-50',
                 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=300&h=300&fit=crop&sat=-30'
             ],
             'klavye': [
                 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=300&h=300&fit=crop&sat=-20',
                 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=300&h=300&fit=crop&sat=-40',
                 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=300&h=300&fit=crop&sat=-60'
             ],
             'kulaklık': [
                 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&sat=-30',
                 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300&h=300&fit=crop&sat=-50',
                 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&sat=-70'
             ],
             'laptop': [
                 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=300&fit=crop&sat=-20',
                 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300&h=300&fit=crop&sat=-40',
                 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=300&fit=crop&sat=-60'
             ],
             'telefon': [
                 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300&h=300&fit=crop',
                 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop&sat=-30',
                 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300&h=300&fit=crop&sat=-50',
                 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop&sat=-70'
             ]
         }
         
         # Kategori için görselleri al
         images = product_images.get(category, [])
         
         # Eğer kategori için görsel yoksa, varsayılan görsel kullan
         if not images:
             return f'https://via.placeholder.com/300x300/2563eb/ffffff?text={category.title()}'
         
        # İndekse göre görsel seç (döngüsel)
        return images[index % len(images)]
    
    def _get_search_url(self, category: str, index: int) -> str:
        """
        Amazon arama URL'leri döndürür.
           
           Args:
               category (str): Ürün kategorisi
               index (int): Ürün indeksi
               
           Returns:
               str: Amazon arama URL'i
           """
        # Kategori bazlı ürün adları
        product_names = {
            'kulaklık': [
                'Anker Soundcore Liberty 4 NC',
                'Sony WF-C700N', 
                'Samsung Galaxy Buds FE',
                'Huawei FreeBuds 5i',
                'JBL Live Pro 2 TWS'
            ],
               'mouse': [
                   'Logitech G203 Lightsync Gaming Mouse',
                   'Razer DeathAdder V2 Gaming Mouse',
                   'SteelSeries Rival 3 Gaming Mouse',
                   'Corsair M65 RGB Elite Gaming Mouse',
                   'HyperX Pulsefire Haste Gaming Mouse'
               ],
               'klavye': [
                   'Logitech G Pro X Mechanical Gaming Keyboard',
                   'Razer BlackWidow V3 Pro Wireless Keyboard',
                   'SteelSeries Apex Pro TKL Gaming Keyboard',
                   'Corsair K100 RGB Mechanical Keyboard',
                   'HyperX Alloy Origins Core Gaming Keyboard'
               ]
           }
           
        # Kategori için ürün adlarını al
        names = product_names.get(category, [])
        
        # Eğer kategori için ürün adı yoksa, genel arama yap
        if not names or index >= len(names):
            return f'https://www.amazon.com.tr/s?k={category}&i=electronics&rh=n%3A12466496031'
        
        # Ürün adını al ve arama URL'i oluştur
        product_name = names[index]
        search_query = product_name.replace(' ', '+')
        return f'https://www.amazon.com.tr/s?k={search_query}&i=electronics&rh=n%3A12466496031'
    
    def _get_mock_product_details(self, asin: str) -> Dict:
        """
        Mock ürün detayları döndürür.
        
        Args:
            asin (str): Ürün ASIN'i
            
        Returns:
            Dict: Mock ürün detayları
        """
        return {
            'asin': asin,
            'title': f'Mock Ürün - {asin}',
            'description': 'Bu bir örnek ürün açıklamasıdır. Gerçek Amazon API anahtarı ile gerçek veriler alabilirsiniz.',
            'price': {
                'current': 299.99,
                'currency': 'TRY',
                'original': 399.99
            },
            'rating': 4.5,
            'reviews_count': 250,
            'images': [
                'https://via.placeholder.com/500x500?text=Ürün+Görseli+1',
                'https://via.placeholder.com/500x500?text=Ürün+Görseli+2'
            ],
            'url': f'https://amazon.com.tr/dp/{asin}',
            'availability': 'Stokta',
            'prime': True,
            'features': [
                'Yüksek kalite',
                'Dayanıklı malzeme',
                'Kolay kullanım',
                'Uzun ömürlü'
            ],
            'specifications': [
                {'name': 'Marka', 'value': 'MockBrand'},
                {'name': 'Model', 'value': 'MockModel'},
                {'name': 'Renk', 'value': 'Siyah'},
                {'name': 'Ağırlık', 'value': '500g'}
            ],
            'reviews': [
                {
                    'rating': 5,
                    'title': 'Harika ürün!',
                    'text': 'Çok memnun kaldım, tavsiye ederim.',
                    'date': '2024-01-15'
                }
            ],
            'variants': [],
            'categories': ['Elektronik', 'Mock Kategori']
        } 