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
database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'swipestyle.db')
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


@app.route('/category-creator')
def category_creator():
    """
    Kategori oluşturucu sayfası
    """
    return render_template('category_creator.html')


@app.route('/status')
def status_page():
    """
    API durumu ve sistem istatistikleri sayfası
    """
    return render_template('status.html')


# ===== API ENDPOINTS =====


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


@app.route('/api/autocomplete', methods=['GET'])
def autocomplete_suggestions():
    """
    Arama için otomatik tamamlama önerilerini döndürür.
    
    Query parametreleri:
    - q: Arama sorgusu
    - language: 'tr' veya 'en' (varsayılan: 'tr')
    - limit: Maksimum sonuç sayısı (varsayılan: 6)
    
    Döner:
    {
        "suggestions": [
            {
                "text": "wireless headphones",
                "icon": "🎧",
                "category": "Audio"
            }
        ]
    }
    """
    query = request.args.get('q', '').strip().lower()
    language = request.args.get('language', 'tr')
    limit = int(request.args.get('limit', 6))
    
    if not query:
        return jsonify({'suggestions': []})
    
    try:
        # Get categories for autocomplete
        categories = category_agent.get_categories(language)
        suggestions = []
        
        # Add category-based suggestions
        for cat in categories:
            if cat['name'].lower().startswith(query):
                suggestions.append({
                    'text': cat['name'],
                    'icon': cat.get('emoji', '🔍'),
                    'category': 'Kategori' if language == 'tr' else 'Category'
                })
        
        # Add predefined popular searches
        popular_searches = {
            'tr': [
                {'text': 'kablosuz kulaklık', 'icon': '🎧', 'category': 'Ses'},
                {'text': 'gaming laptop', 'icon': '💻', 'category': 'Bilgisayar'},
                {'text': 'akıllı telefon', 'icon': '📱', 'category': 'Mobil'},
                {'text': 'bluetooth hoparlör', 'icon': '🔊', 'category': 'Ses'},
                {'text': 'tablet', 'icon': '📱', 'category': 'Mobil'},
                {'text': 'akıllı saat', 'icon': '⌚', 'category': 'Giyilebilir'},
                {'text': 'drone', 'icon': '🚁', 'category': 'Hobi'},
                {'text': 'kamera', 'icon': '📷', 'category': 'Fotoğraf'},
                {'text': 'oyuncu klavyesi', 'icon': '⌨️', 'category': 'Gaming'},
                {'text': 'gaming mouse', 'icon': '🖱️', 'category': 'Gaming'},
                {'text': 'powerbank', 'icon': '🔋', 'category': 'Aksesuar'},
                {'text': 'wifi router', 'icon': '📶', 'category': 'Ağ'},
                {'text': 'harici disk', 'icon': '💾', 'category': 'Depolama'},
                {'text': 'mikrofon', 'icon': '🎤', 'category': 'Ses'},
                {'text': 'web kamerası', 'icon': '📹', 'category': 'Video'},
                {'text': 'vr gözlük', 'icon': '🥽', 'category': 'VR'},
                {'text': 'akıllı tv', 'icon': '📺', 'category': 'Ev'},
                {'text': 'konsol', 'icon': '🎮', 'category': 'Gaming'},
                {'text': 'fitness tracker', 'icon': '⌚', 'category': 'Sağlık'}
            ],
            'en': [
                {'text': 'wireless headphones', 'icon': '🎧', 'category': 'Audio'},
                {'text': 'gaming laptop', 'icon': '💻', 'category': 'Computer'},
                {'text': 'smartphone', 'icon': '📱', 'category': 'Mobile'},
                {'text': 'bluetooth speaker', 'icon': '🔊', 'category': 'Audio'},
                {'text': 'tablet', 'icon': '📱', 'category': 'Mobile'},
                {'text': 'smartwatch', 'icon': '⌚', 'category': 'Wearable'},
                {'text': 'drone', 'icon': '🚁', 'category': 'Hobby'},
                {'text': 'camera', 'icon': '📷', 'category': 'Photo'},
                {'text': 'gaming keyboard', 'icon': '⌨️', 'category': 'Gaming'},
                {'text': 'gaming mouse', 'icon': '🖱️', 'category': 'Gaming'},
                {'text': 'power bank', 'icon': '🔋', 'category': 'Accessory'},
                {'text': 'wifi router', 'icon': '📶', 'category': 'Network'},
                {'text': 'external drive', 'icon': '💾', 'category': 'Storage'},
                {'text': 'microphone', 'icon': '🎤', 'category': 'Audio'},
                {'text': 'webcam', 'icon': '📹', 'category': 'Video'},
                {'text': 'vr headset', 'icon': '🥽', 'category': 'VR'},
                {'text': 'smart tv', 'icon': '📺', 'category': 'Home'},
                {'text': 'gaming console', 'icon': '🎮', 'category': 'Gaming'},
                {'text': 'fitness tracker', 'icon': '⌚', 'category': 'Health'}
            ]
        }
        
        # Add popular searches that match the query
        for item in popular_searches.get(language, popular_searches['en']):
            if item['text'].lower().startswith(query) and len(suggestions) < limit:
                # Avoid duplicates
                if not any(s['text'].lower() == item['text'].lower() for s in suggestions):
                    suggestions.append(item)
        
        # Limit results
        suggestions = suggestions[:limit]
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        logger.error(f"Error getting autocomplete suggestions: {e}")
        return jsonify({'suggestions': []})


@app.route('/api/search-category', methods=['POST'])
def search_category():
    """
    Kategori arama ve otomatik oluşturma.
    
    POST isteği bekler:
    {
        "query": "gaming chairs",
        "language": "tr" | "en",
        "session_id": "optional"
    }
    
    Döner:
    {
        "success": true,
        "category": {
            "name": "Gaming Chairs",
            "emoji": "🪑",
            "specs": [...]
        },
        "created": true
    }
    """
    data = request.json
    query = data.get('query', '').strip()
    session_id = data.get('session_id') or session.get('session_id') or str(uuid.uuid4())
    session['session_id'] = session_id
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    # Kullanıcı ayarlarını al
    user_settings = category_agent.get_user_settings(session_id)
    language = data.get('language', user_settings.get('language', 'tr'))
    
    try:
        logger.info(f"Search Category - Query: '{query}' (Language: {language})")
        
        # Try to find or create the category
        category, created = category_agent.get_or_create_category(query, language)
        
        if category:
            category_dict = category.to_dict(language)
            
            message = {
                'tr': f"Kategori {'oluşturuldu' if created else 'bulundu'}: {category.name}",
                'en': f"Category {'created' if created else 'found'}: {category.name}"
            }
            
            return jsonify({
                'success': True,
                'category': category_dict,
                'created': created,
                'message': message[language],
                'session_id': session_id
            })
        else:
            error_message = {
                'tr': f"'{query}' kategorisi bulunamadı veya oluşturulamadı.",
                'en': f"Category '{query}' could not be found or created."
            }
            return jsonify({
                'success': False,
                'error': error_message[language]
            }), 404
            
    except Exception as e:
        logger.error(f"Search category error: {e}")
        error_message = {
            'tr': f"Kategori arama hatası: {str(e)}",
            'en': f"Category search error: {str(e)}"
        }
        return jsonify({
            'success': False,
            'error': error_message[language]
        }), 500


@app.route('/api/category-images', methods=['GET'])
def get_category_images():
    """
    Kategori için Google Images'dan resim URL'lerini döndürür.
    
    Query parametreleri:
    - category: Kategori adı (zorunlu)
    - max_images: Maksimum resim sayısı (varsayılan: 3)
    
    Döner:
    {
        "images": ["url1", "url2", "url3"],
        "category": "Electronics"
    }
    """
    category = request.args.get('category', '').strip()
    max_images = int(request.args.get('max_images', 3))
    
    if not category:
        return jsonify({'error': 'Category parameter is required'}), 400
    
    try:
        # Get category images from enhanced category agent
        images = category_agent.get_category_images(category, max_images)
        
        return jsonify({
            'images': images,
            'category': category,
            'count': len(images)
        })
        
    except Exception as e:
        logger.error(f"Error getting category images: {e}")
        return jsonify({'error': 'Failed to get category images'}), 500


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


@app.route('/api/category-creator', methods=['POST'])
def category_creator_agent():
    """
    Kategori Oluşturucu Agent - Girilen kategori için otomatik soru ve emoji üretir.
    
    POST isteği bekler:
    {
        "category_name": "Gaming Chairs",
        "language": "tr" | "en",
        "force_create": false,
        "session_id": "optional"
    }
    
    Döner:
    {
        "success": true,
        "category": {
            "name": "Gaming Chairs",
            "emoji": "🪑",
            "questions": [
                {
                    "question": "Ergonomik tasarım önemli mi?",
                    "key": "Ergonomic",
                    "emoji": "🧘"
                }
            ]
        },
        "created": true,
        "message": "Kategori başarıyla oluşturuldu!"
    }
    """
    data = request.json
    category_name = data.get('category_name', '').strip()
    language = data.get('language', 'tr')
    force_create = data.get('force_create', False)
    session_id = data.get('session_id') or session.get('session_id') or str(uuid.uuid4())
    session['session_id'] = session_id
    
    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400
    
    try:
        logger.info(f"Category Creator Agent - Processing: {category_name} (Language: {language})")
        
        # Check if category already exists
        existing_category, _ = category_agent.get_or_create_category(category_name, language)
        
        if existing_category and not force_create:
            # Category already exists
            category_dict = existing_category.to_dict(language)
            message = {
                'tr': f"'{category_name}' kategorisi zaten mevcut. {len(category_dict.get('specs', []))} soru bulundu.",
                'en': f"Category '{category_name}' already exists. Found {len(category_dict.get('specs', []))} questions."
            }
            
            return jsonify({
                'success': True,
                'category': category_dict,
                'created': False,
                'already_exists': True,
                'message': message[language],
                'session_id': session_id
            })
        
        # Create new category or force recreate
        if force_create and existing_category:
            # Delete existing category specs and recreate
            from app.models import CategorySpec
            CategorySpec.query.filter_by(category_id=existing_category.id).delete()
            db.session.commit()
            logger.info(f"Forcing recreation of category: {category_name}")
        
        # Generate new category with AI
        category, created = category_agent.get_or_create_category(category_name, language)
        
        if category:
            category_dict = category.to_dict(language)
            
            message = {
                'tr': f"'{category_name}' kategorisi başarıyla oluşturuldu! {len(category_dict.get('specs', []))} soru üretildi.",
                'en': f"Category '{category_name}' successfully created! Generated {len(category_dict.get('specs', []))} questions."
            }
            
            # Log the created questions
            specs = category_dict.get('specs', [])
            logger.info(f"Generated {len(specs)} questions for '{category_name}':")
            for i, spec in enumerate(specs, 1):
                logger.info(f"  {i}. {spec.get('question', 'N/A')} ({spec.get('emoji', '❓')})")
            
            return jsonify({
                'success': True,
                'category': category_dict,
                'created': True,
                'message': message[language],
                'session_id': session_id,
                'questions_count': len(specs)
            })
        else:
            error_message = {
                'tr': f"'{category_name}' kategorisi oluşturulamadı. AI servisi kullanılamıyor olabilir.",
                'en': f"Failed to create category '{category_name}'. AI service may be unavailable."
            }
            return jsonify({
                'success': False,
                'error': error_message[language]
            }), 500
            
    except Exception as e:
        logger.error(f"Category Creator Agent error: {e}")
        error_message = {
            'tr': f"Kategori oluşturulurken hata oluştu: {str(e)}",
            'en': f"Error creating category: {str(e)}"
        }
        return jsonify({
            'success': False,
            'error': error_message[language]
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    """404 hata sayfası"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.route('/api/status')
def api_status():
    """
    API durumu ve kullanım istatistiklerini döndürür.
    
    Returns:
        JSON: API durumu, günlük kullanım ve limitleri
    """
    try:
        from datetime import date
        
        status_info = {
            'api_available': category_agent.model is not None,
            'daily_usage': getattr(category_agent, 'daily_api_calls', 0),
            'daily_limit': getattr(category_agent, 'daily_limit', 50),
            'current_date': str(date.today()),
            'cache_size': len(getattr(category_agent, 'translation_cache', {})),
            'system_status': 'operational'
        }
        
        # Limit kontrolü
        remaining = status_info['daily_limit'] - status_info['daily_usage']
        status_info['remaining_calls'] = max(0, remaining)
        status_info['limit_reached'] = remaining <= 0
        
        return jsonify(status_info)
        
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({
            'error': 'Could not retrieve status',
            'system_status': 'error'
        }), 500


@app.errorhandler(404)
def not_found(error):
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
