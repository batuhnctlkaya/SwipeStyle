#!/usr/bin/env python3
"""
Amazon API Entegrasyon Test Dosyası
===================================

Bu dosya, Amazon API entegrasyonunun doğru çalışıp çalışmadığını test eder.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.amazon_api import AmazonAPI
from app.product_search import ProductSearch

def test_amazon_api():
    """Amazon API'sini test eder"""
    print("🧪 Amazon API Testi Başlıyor...")
    print("=" * 50)
    
    # Amazon API'sini başlat
    api = AmazonAPI()
    
    # Test 1: Ürün arama
    print("📦 Test 1: Ürün Arama")
    products = api.search_products("laptop", max_results=3)
    print(f"   Bulunan ürün sayısı: {len(products)}")
    
    if products:
        print("   İlk ürün:")
        product = products[0]
        print(f"     Başlık: {product.get('title', 'N/A')}")
        print(f"     Fiyat: {product.get('price', {}).get('current', 'N/A')} {product.get('price', {}).get('currency', 'TRY')}")
        print(f"     ASIN: {product.get('asin', 'N/A')}")
    
    # Test 2: Ürün detayları
    print("\n📋 Test 2: Ürün Detayları")
    if products:
        asin = products[0].get('asin', 'MOCK001')
        details = api.get_product_details(asin)
        if details:
            print(f"   Ürün detayları alındı: {details.get('title', 'N/A')}")
        else:
            print("   ❌ Ürün detayları alınamadı")
    
    print("\n✅ Amazon API Testi Tamamlandı!")

def test_product_search():
    """ProductSearch modülünü test eder"""
    print("\n🔍 ProductSearch Testi Başlıyor...")
    print("=" * 50)
    
    # ProductSearch'ü başlat
    search = ProductSearch()
    
    # Test 1: Tercih bazlı arama
    print("🎯 Test 1: Tercih Bazlı Arama")
    category = "Laptop"
    preferences = ["Programlama", "25-40k₺"]
    language = "tr"
    
    products = search.search_by_preferences(
        category=category,
        preferences=preferences,
        language=language,
        max_results=3
    )
    
    print(f"   Kategori: {category}")
    print(f"   Tercihler: {preferences}")
    print(f"   Bulunan ürün sayısı: {len(products)}")
    
    if products:
        print("   İlk ürün:")
        product = products[0]
        print(f"     Başlık: {product.get('title', 'N/A')}")
        print(f"     Fiyat: {product.get('price', {}).get('current', 'N/A')} {product.get('price', {}).get('currency', 'TRY')}")
    
    # Test 2: Fiyat aralığı çıkarma
    print("\n💰 Test 2: Fiyat Aralığı Çıkarma")
    test_preferences = ["Akülü", "5.000-10.000₺", "Bluetooth"]
    min_price, max_price = search._get_price_range(test_preferences, "tr")
    print(f"   Tercihler: {test_preferences}")
    print(f"   Çıkarılan fiyat aralığı: {min_price} - {max_price} TRY")
    
    # Test 3: Anahtar kelime çıkarma
    print("\n🔤 Test 3: Anahtar Kelime Çıkarma")
    test_text = "Akülü (Kablosuz, taşınabilir)"
    keywords = search._extract_keywords(test_text, "tr")
    print(f"   Metin: {test_text}")
    print(f"   Çıkarılan anahtar kelimeler: {keywords}")
    
    print("\n✅ ProductSearch Testi Tamamlandı!")

def test_integration():
    """Tam entegrasyon testi"""
    print("\n🚀 Tam Entegrasyon Testi Başlıyor...")
    print("=" * 50)
    
    # Agent'ı test et
    try:
        from app.agent import Agent
        agent = Agent()
        
        # Test verisi
        test_data = {
            'step': 1,
            'category': 'Headphones',
            'answers': ['Kulak içi (Taşınabilir)', 'Evet', '1.5-3k₺'],
            'language': 'tr'
        }
        
        print("🤖 Agent Testi")
        response = agent.handle(test_data)
        
        if response.get('type') == 'recommendation':
            print("   ✅ Öneriler oluşturuldu")
            recommendations = response.get('recommendations', [])
            amazon_products = response.get('amazon_products', [])
            print(f"   AI öneri sayısı: {len(recommendations)}")
            print(f"   Amazon ürün sayısı: {len(amazon_products)}")
        else:
            print(f"   ❌ Beklenmeyen yanıt: {response.get('type')}")
    
    except Exception as e:
        print(f"   ❌ Agent testi hatası: {e}")
    
    print("\n✅ Tam Entegrasyon Testi Tamamlandı!")

if __name__ == "__main__":
    print("🎯 SwipeStyle Amazon Entegrasyon Testi")
    print("=" * 60)
    
    try:
        test_amazon_api()
        test_product_search()
        test_integration()
        
        print("\n🎉 Tüm testler başarıyla tamamlandı!")
        print("\n📝 Not: Eğer mock veriler görüyorsanız, RAINFOREST_API_KEY environment variable'ını ayarlayın.")
        print("   Rainforest API'den ücretsiz anahtar alabilirsiniz: https://www.rainforestapi.com/")
        
    except Exception as e:
        print(f"\n❌ Test sırasında hata oluştu: {e}")
        import traceback
        traceback.print_exc() 