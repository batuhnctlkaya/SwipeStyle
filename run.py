"""
SwipeStyle Ana Uygulama Dosyası
================================

Bu dosya, SwipeStyle ürün tavsiye sisteminin ana Flask uygulamasını içerir.
Sistem, kullanıcıların teknoloji ürünleri için kişiselleştirilmiş öneriler almasını sağlar.

Ana Özellikler:
- Akıllı kategori tespiti ve oluşturma
- Dinamik soru-cevap tabanlı ürün filtreleme
- Gemini AI entegrasyonu ile akıllı öneriler
- Web arayüzü desteği
- Çok dilli destek (Türkçe/İngilizce)

API Endpoint'leri:
- /detect_category: Kullanıcı sorgusundan kategori tespiti
- /search/<query>: Akıllı kategori arama
- /categories: Mevcut kategorileri listele
- /ask: Soru-cevap akışını yönet
- /: Ana web sayfası

Gereksinimler:
- Flask web framework
- Google Generative AI (Gemini)
- .env dosyasında GEMINI_API_KEY tanımlı olmalı

Kullanım:
    python run.py
    # Uygulama http://localhost:8080 adresinde çalışır
"""

# Standard imports
import json
import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import app modules
from app.agent import Agent
from app.agent import detect_category_from_query
from app.category_generator import add_dynamic_category_route

app = Flask(__name__, static_folder='website')
agent = Agent()

# Dinamik kategori oluşturma özelliğini ekle
add_dynamic_category_route(app)

@app.route('/detect_category', methods=['POST'])
def detect_category():
    """
    Kullanıcı sorgusundan kategori tespiti yapar.
    
    Bu endpoint, kullanıcının yazdığı metni analiz ederek
    en uygun ürün kategorisini tespit eder. Gerekirse yeni kategori oluşturur.
    
    POST isteği bekler:
    {
        "query": "kablosuz kulaklık"
    }
    
    Döner:
    {
        "category": "Headphones"
    }
    
    Eğer kategori mevcut değilse, akıllı kategori tespiti sistemi
    kullanarak yeni kategori oluşturur.
    """
    data = request.json
    print("=" * 50)
    print("🔍 /detect_category endpointine gelen veri:", data)
    print("=" * 50)
    # Dosyaya da yazadıralım
    with open('debug_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"🔍 /detect_category veri: {data}\n")
    query = data.get('query', '')
    category = detect_category_from_query(query)
    return jsonify({'category': category})

@app.route('/')
def index():
    """
    Ana web sayfasını döndürür.
    
    Bu endpoint, kullanıcıların ürün arama ve kategori seçimi
    yapabileceği ana arayüzü sunar.
    
    Returns:
        HTML: Ana web sayfası
    """
    return app.send_static_file('main.html')

@app.route('/<path:filename>')
def static_files(filename):
    """
    Statik dosyaları (CSS, JS, resimler) sunar.
    
    Bu endpoint, web sitesinin statik dosyalarını (JavaScript,
    CSS, resimler vb.) sunar.
    
    Args:
        filename: İstenen dosya adı
        
    Returns:
        İstenen statik dosya
    """
    return send_from_directory(app.static_folder, filename)

@app.route('/categories')
def get_categories():
    """
    Mevcut tüm kategorileri ve özelliklerini döndürür.
    
    Bu endpoint, frontend'in kategori listesini göstermesi
    için kullanılır. Her kategori için soru ve emoji bilgilerini içerir.
    
    Returns:
        JSON: Kategori listesi ve özellikleri
    """
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    return jsonify(categories)

@app.route('/ask', methods=['POST'])
def ask():
    """
    Soru-cevap akışını yönetir ve ürün önerileri döndürür.
    
    Bu endpoint, kullanıcının kategori seçiminden sonra
    adım adım sorular sorar ve sonunda ürün önerileri sunar.
    
    POST isteği bekler:
    {
        "step": 1,
        "category": "Headphones", 
        "answers": ["Yes", "No"],
        "language": "tr"
    }
    
    Döner:
    - Soru varsa: {"question": "...", "options": ["Yes", "No"], "emoji": "🎧"}
    - Öneriler varsa: {"recommendations": [...], "amazon_products": [...]}
    - Hata varsa: {"error": "..."}
    
    Özellikler:
    - Dinamik soru akışı
    - Tercih analizi
    - Güven skoru hesaplama
    - Amazon ürün entegrasyonu
    - Çok dilli destek
    """
    data = request.json
    print("=" * 50)
    print("📩 /ask endpointine gelen veri:", data)
    print("=" * 50)
    # Dosyaya da yazdıralım
    with open('debug_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"📩 /ask veri: {data}\n")
    response = agent.handle(data)
    return jsonify(response)

@app.route('/amazon/product/<asin>', methods=['GET'])
def get_amazon_product(asin):
    """
    Amazon ürün detaylarını döndürür.
    
    Bu endpoint, belirli bir Amazon ürününün detaylı bilgilerini çeker.
    
    Args:
        asin: Amazon ASIN kodu
        
    Returns:
        JSON: Ürün detayları
    """
    try:
        try:
            from app.amazon_api import AmazonAPI
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Amazon API modülü bulunamadı'
            }), 500
        
        api = AmazonAPI()
        product_details = api.get_product_details(asin)
        
        if product_details:
            return jsonify({
                'success': True,
                'product': product_details
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ürün bulunamadı'
            }), 404
            
    except Exception as e:
        print(f"❌ Amazon ürün detay hatası: {e}")
        return jsonify({
            'success': False,
            'error': 'Ürün detayları alınamadı'
        }), 500

@app.route('/amazon/search', methods=['POST'])
def search_amazon_products():
    """
    Amazon'da ürün arama yapar.
    
    POST isteği bekler:
    {
        "query": "laptop",
        "max_results": 10,
        "min_price": 1000,
        "max_price": 5000
    }
    
    Returns:
        JSON: Bulunan ürünler
    """
    try:
        try:
            from app.amazon_api import AmazonAPI
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Amazon API modülü bulunamadı'
            }), 500
        
        data = request.json
        query = data.get('query', '')
        max_results = data.get('max_results', 10)
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        api = AmazonAPI()
        products = api.search_products(
            query=query,
            max_results=max_results,
            min_price=min_price,
            max_price=max_price
        )
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
        
    except Exception as e:
        print(f"❌ Amazon arama hatası: {e}")
        return jsonify({
            'success': False,
            'error': 'Arama yapılamadı'
        }), 500

if __name__ == '__main__':
    """
    Uygulamayı geliştirme modunda başlatır.
    
    Debug modu açık, Render için PORT environment variable kullanır.
    Production ortamında debug=False yapılmalıdır.
    """
    # Render deployment için PORT environment variable kullan
    port = int(os.environ.get('PORT', 8082))
    app.run(debug=False, host='0.0.0.0', port=port)