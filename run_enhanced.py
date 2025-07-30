#!/usr/bin/env python3
"""
SwipeStyle AI - Enhanced Version with Multi-language Support and Shopping Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bu script, SwipeStyle AI uygulamasının gelişmiş versiyonunu çalıştırır.
Çok dilli destek, ülke seçimi ve Google Shopping entegrasyonu içerir.

Özellikler:
- Türkçe/İngilizce dil desteği
- Ülke bazlı alışveriş (TR, US, GB, DE, FR)
- Google Shopping API entegrasyonu
- Kullanıcı oturum yönetimi
- Dinamik kategori oluşturma
- Gerçek zamanlı çeviri
"""

from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
import uuid
import os
import logging

# Import our enhanced modules
from app.enhanced_category_agent import EnhancedDatabaseCategoryAgent
from app.models import db, CategorySpec, UserSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='website',
            static_folder='website')

# Enable CORS for all domains (adjust for production)
CORS(app)

# Secret key for sessions (use environment variable in production)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
database_path = os.path.join(os.path.dirname(__file__), 'instance', 'swipestyle.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize enhanced category agent
try:
    category_agent = EnhancedDatabaseCategoryAgent()
    logger.info("Enhanced category agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize enhanced category agent: {e}")
    # Fallback to basic agent if enhanced fails
    from app.database_category_agent import DatabaseCategoryAgent
    category_agent = DatabaseCategoryAgent()
    logger.info("Fallback to basic database category agent")

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


@app.route('/')
def index():
    """
    Ana sayfa - Gelişmiş SwipeStyle arayüzünü sunar.
    
    Çok dilli destek ve alışveriş entegrasyonu ile
    modern bir kullanıcı deneyimi sağlar.
    """
    return render_template('main_enhanced.html')


@app.route('/main_enhanced.js')
def main_enhanced_js():
    """JavaScript dosyasını servis eder."""
    from flask import send_from_directory
    return send_from_directory('website', 'main_enhanced.js', mimetype='application/javascript')


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    Mevcut kategorileri döndürür.
    
    Query parametreleri:
    - language: 'tr' veya 'en' (varsayılan: 'tr')
    
    Döner:
    {
        "categories": [
            {"name": "Headphones", "emoji": "🎧"},
            ...
        ]
    }
    """
    language = request.args.get('language', 'tr')
    session_id = session.get('session_id') or str(uuid.uuid4())
    session['session_id'] = session_id
    
    try:
        categories = category_agent.get_categories(language)
        return jsonify({'categories': categories})
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({'error': 'Failed to get categories'}), 500


@app.route('/api/user-settings', methods=['GET', 'POST'])
def user_settings():
    """
    Kullanıcı ayarlarını yönetir.
    
    GET: Mevcut ayarları döndürür
    POST: Yeni ayarları kaydeder
    
    POST body:
    {
        "language": "tr" | "en",
        "country": "TR" | "US" | "GB" | "DE" | "FR"
    }
    """
    session_id = session.get('session_id') or str(uuid.uuid4())
    session['session_id'] = session_id
    
    if request.method == 'GET':
        try:
            settings = category_agent.get_user_settings(session_id)
            return jsonify(settings)
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return jsonify({'error': 'Failed to get user settings'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            settings = category_agent.save_user_settings(
                session_id,
                data.get('language', 'tr'),
                data.get('country', 'TR')
            )
            return jsonify(settings)
        except Exception as e:
            logger.error(f"Error saving user settings: {e}")
            return jsonify({'error': 'Failed to save user settings'}), 500


@app.route('/api/ask', methods=['POST'])
def ask():
    """
    Soru-cevap akışını yönetir.
    
    POST isteği bekler:
    {
        "step": 1,
        "category": "Headphones",
        "answers": ["Yes", "No"],
        "language": "tr" | "en",
        "session_id": "optional"
    }
    
    Döner:
    - Soru varsa: {"question": "...", "options": ["Yes", "No"], "emoji": "🎧"}
    - Öneriler varsa: {"recommendations": [...]}
    - Hata varsa: {"error": "..."}
    """
    data = request.json
    session_id = data.get('session_id') or session.get('session_id') or str(uuid.uuid4())
    session['session_id'] = session_id
    
    # Kullanıcı ayarlarını al
    user_settings = category_agent.get_user_settings(session_id)
    language = data.get('language', user_settings.get('language', 'tr'))
    
    try:
        response = category_agent.handle(data, language=language, session_id=session_id)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error handling question: {e}")
        return jsonify({'error': 'Failed to process question'}), 500


@app.route('/api/shopping', methods=['POST'])
def shopping_recommendations():
    """
    Google Shopping'ten ürün önerileri getirir.
    
    POST isteği bekler:
    {
        "query": "wireless headphones",
        "country": "US",
        "language": "en",
        "session_id": "optional"
    }
    
    Döner:
    {
        "query": "wireless headphones",
        "country": "US",
        "language": "en",
        "total_results": 8,
        "products": [
            {
                "title": "Product Name",
                "price": "$99.99",
                "source": "Store Name",
                "link": "https://...",
                "thumbnail": "https://...",
                "rating": 4.5,
                "reviews": 150
            }
        ]
    }
    """
    data = request.json
    query = data.get('query', '')
    session_id = data.get('session_id') or session.get('session_id') or str(uuid.uuid4())
    
    # Session ID'yi kaydet
    session['session_id'] = session_id
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    # Kullanıcı ayarlarını al
    user_settings = category_agent.get_user_settings(session_id)
    country = data.get('country', user_settings.get('country', 'TR'))
    language = data.get('language', user_settings.get('language', 'tr'))
    
    try:
        # Shopping önerilerini getir
        recommendations = category_agent.get_shopping_recommendations(query, country, language)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting shopping recommendations: {e}")
        return jsonify({'error': 'Failed to get shopping recommendations'}), 500


@app.route('/api/create-category', methods=['POST'])
def create_category():
    """
    Yeni bir kategori oluşturur (AI destekli).
    
    POST isteği bekler:
    {
        "category_name": "Smart Watches",
        "language": "tr" | "en",
        "session_id": "optional"
    }
    
    Döner:
    {
        "success": true,
        "category": {
            "name": "Smart Watches",
            "emoji": "⌚",
            "questions": [...]
        }
    }
    """
    data = request.json
    category_name = data.get('category_name', '')
    session_id = data.get('session_id') or session.get('session_id') or str(uuid.uuid4())
    session['session_id'] = session_id
    
    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400
    
    # Kullanıcı ayarlarını al
    user_settings = category_agent.get_user_settings(session_id)
    language = data.get('language', user_settings.get('language', 'tr'))
    
    try:
        category, created = category_agent.get_or_create_category(category_name, language)
        if category:
            return jsonify({
                'success': True,
                'category': category.to_dict(language),
                'created': created,
                'session_id': session_id
            })
        else:
            return jsonify({'error': 'Failed to create category'}), 500
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return jsonify({'error': 'Failed to create category'}), 500


@app.errorhandler(404)
def not_found_error(error):
    """404 hata sayfası"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 hata sayfası"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    """
    Gelişmiş SwipeStyle uygulamasını başlatır.
    
    Özellikler:
    - Çok dilli destek (TR/EN)
    - Ülke bazlı alışveriş
    - Google Shopping entegrasyonu
    - Kullanıcı oturum yönetimi
    - AI destekli kategori oluşturma
    """
    print("🚀 Starting SwipeStyle AI Enhanced Server...")
    print("📊 Features: Multi-language, Shopping Integration, AI Categories")
    print("🌐 Access: http://localhost:8082")
    print("📱 Languages: Turkish (TR) / English (EN)")
    print("🛒 Countries: TR, US, GB, DE, FR")
    print("-" * 60)
    
    app.run(debug=True, port=8082, host='0.0.0.0')
