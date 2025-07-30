"""
SwipeStyle Ana Uygulama Dosyası
================================

Bu dosya, SwipeStyle ürün tavsiye sisteminin ana Flask uygulamasını içerir.
Sistem, kullanıcıların teknoloji ürünleri için kişiselleştirilmiş öneriler almasını sağlar.

Ana Özellikler:
- Kategori tespiti ve oluşturma
- Soru-cevap tabanlı ürün filtreleme
- Gemini AI entegrasyonu ile akıllı öneriler
- Web arayüzü desteği

API Endpoint'leri:
- /detect_category: Kullanıcı sorgusundan kategori tespiti
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

# Ensure requirements are installed at startup
import subprocess
import sys
import os

def install_requirements():
    """
    Uygulama başlangıcında gerekli paketlerin kurulu olduğundan emin olur.
    
    Bu fonksiyon, requirements.txt dosyasındaki tüm bağımlılıkları
    otomatik olarak kurar. Eğer paketler zaten kuruluysa, 
    pip bunu atlar ve hata vermez.
    """
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])

install_requirements()

import json
from flask import Flask, request, jsonify, send_from_directory
from app.agent import Agent
from app.category_agent import CategoryAgent

# Flask uygulamasını başlat
app = Flask(__name__, static_folder='website')
category_agent = CategoryAgent()
agent = Agent()

@app.route('/detect_category', methods=['POST'])
def detect_category():
    """
    Kullanıcı sorgusundan kategori tespiti yapar.
    
    POST isteği bekler:
    {
        "query": "kablosuz kulaklık"
    }
    
    Döner:
    {
        "category": "Headphones",
        "created": false
    }
    
    Eğer kategori mevcut değilse, Gemini AI kullanarak yeni kategori oluşturur.
    """
    data = request.json
    query = data.get('query', '')
    # Use CategoryAgent to get or create the category
    category, created = category_agent.get_or_create_category(query)
    if not category:
        return jsonify({'error': 'Kategori oluşturulamadı veya tespit edilemedi. Lütfen daha açık bir istek girin veya daha sonra tekrar deneyin.'}), 400
    return jsonify({'category': category, 'created': created})

@app.route('/')
def index():
    """
    Ana web sayfasını döndürür.
    
    Bu endpoint, kullanıcıların ürün arama ve kategori seçimi
    yapabileceği ana arayüzü sunar.
    """
    return app.send_static_file('main.html')

# Serve static files (main.js, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    """
    Statik dosyaları (CSS, JS, resimler) sunar.
    
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
        JSON formatında kategori listesi
    """
    # Use CategoryAgent to get categories and their specs
    cats = category_agent.categories
    return jsonify(cats)

@app.route('/ask', methods=['POST'])
def ask():
    """
    Soru-cevap akışını yönetir ve ürün önerileri döndürür.
    
    POST isteği bekler:
    {
        "step": 1,
        "category": "Headphones", 
        "answers": ["Yes", "No"]
    }
    
    Döner:
    - Soru varsa: {"question": "...", "options": ["Yes", "No"], "emoji": "🎧"}
    - Öneriler varsa: {"recommendations": [...]}
    - Hata varsa: {"error": "..."}
    
    Bu endpoint, kullanıcının kategori seçiminden sonra
    adım adım sorular sorar ve sonunda ürün önerileri sunar.
    """
    data = request.json
    response = agent.handle(data)
    return jsonify(response)

if __name__ == '__main__':
    """
    Uygulamayı geliştirme modunda başlatır.
    
    Debug modu açık, port 8080'de çalışır.
    Production ortamında debug=False yapılmalıdır.
    """
    app.run(debug=True, port=8080)