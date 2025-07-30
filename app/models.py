"""
SwipeStyle Veritabanı Modelleri
================================

Bu modül, SwipeStyle uygulamasının veritabanı modellerini içerir.
SQLAlchemy ORM kullanarak kategoriler ve özellikler için veri yapıları tanımlar.

Ana Sınıflar:
- Category: Kategori modeli (Mouse, Headphones, vb.)
- CategorySpec: Kategori özelliği modeli (Kablosuz, ANC, vb.)

Veritabanı İlişkileri:
- Bir kategori birden fazla özelliğe sahip olabilir (1:N)
- Her özellik bir kategoriye ait olmalıdır

Özellikler:
- Otomatik tablo oluşturma
- UTF-8 karakter desteği (Türkçe)
- JSON uyumlu veri yapıları
- Foreign key ilişkileri

Kullanım:
    from app.models import db, Category, CategorySpec
    db.create_all()  # Tabloları oluştur
"""

from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Category(db.Model):
    """
    Kategori Modeli
    
    Ürün kategorilerini saklar (örn: Phones, Laptops, Headphones).
    Her kategorinin kendine ait özellik soruları olabilir.
    
    Alanlar:
    - id: Otomatik artan birincil anahtar  
    - name: Kategori adı
    - created_at: Oluşturulma zamanı
    - specs: Bu kategoriye ait özellikler (1:N ilişki)
    
    Örnek:
        category = Category(name="Headphones")
        db.session.add(category)
        db.session.commit()
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # İlişki: Bu kategoriye ait özellikler
    specs = db.relationship('CategorySpec', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self, language='tr'):
        """
        Kategoriyi JSON uyumlu sözlük formatına çevirir.
        
        Args:
            language (str): Dil seçimi ('tr' veya 'en')
        
        Returns:
            dict: Kategori bilgileri içeren sözlük
            
        Format:
            {
                "id": 1,
                "name": "Headphones",
                "specs": [
                    {
                        "id": 1,
                        "key": "Kablosuz",
                        "question": "Kablosuz kulaklık ister misiniz?",
                        "emoji": "🎧"
                    }
                ]
            }
        """
        return {
            'id': self.id,
            'name': self.name,
            'specs': [spec.to_dict(language) for spec in self.specs]
        }


class UserSettings(db.Model):
    """
    Kullanıcı Ayarları Modeli
    
    Kullanıcıların dil ve ülke tercihlerini saklar.
    Session tabanlı veya IP tabanlı takip için kullanılabilir.
    
    Alanlar:
    - id: Otomatik artan birincil anahtar
    - session_id: Oturum ID'si (session tracking için)
    - language: Dil tercihi ('tr' veya 'en')
    - country: Ülke kodu ('TR', 'US', 'GB', vb.)
    - created_at: Oluşturulma zamanı
    - updated_at: Güncellenme zamanı
    """
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    language = db.Column(db.String(2), nullable=False, default='tr')  # 'tr' or 'en'
    country = db.Column(db.String(2), nullable=False, default='TR')   # Country code like 'TR', 'US', etc.
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<UserSettings {self.session_id}: {self.language}/{self.country}>'
    
    def to_dict(self):
        """
        Ayarları JSON uyumlu sözlük formatına çevirir.
        
        Returns:
            dict: Ayar bilgileri içeren sözlük
        """
        return {
            'session_id': self.session_id,
            'language': self.language,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CategorySpec(db.Model):
    """
    Kategori Özelliği Modeli
    
    Her kategori için sorulacak soruları ve özelliklerini saklar.
    Her özellik bir kategoriye bağlıdır (N:1 ilişki).
    
    Alanlar:
    - id: Otomatik artan birincil anahtar
    - category_id: Kategori ID'si (foreign key)
    - key: Özellik anahtarı (örn: "Kablosuz", "ANC")
    - question_tr: Türkçe soru metni
    - question_en: İngilizce soru metni
    - emoji: Soru ile birlikte gösterilecek emoji
    
    Örnek:
        spec = CategorySpec(
            category_id=1,
            key="Kablosuz",
            question_tr="Kablosuz kulaklık ister misiniz?",
            question_en="Do you want wireless headphones?",
            emoji="🎧"
        )
        db.session.add(spec)
        db.session.commit()
    """
    __tablename__ = 'category_specs'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)     # Legacy question field (for backward compatibility)
    question_tr = db.Column(db.Text, nullable=False)  # Turkish question
    question_en = db.Column(db.Text, nullable=True)   # English question (can be auto-translated)
    emoji = db.Column(db.String(10), nullable=False)
    question_type = db.Column(db.String(20), nullable=False, default='yesno')  # 'yesno' or 'choice'
    options = db.Column(db.Text, nullable=True)  # JSON string of options for choice questions
    
    def __repr__(self):
        return f'<CategorySpec {self.key} for {self.category.name}>'
    
    def to_dict(self, language='tr'):
        """
        Özelliği JSON uyumlu sözlük formatına çevirir.
        
        Args:
            language (str): Dil seçimi ('tr' veya 'en')
        
        Returns:
            dict: Özellik bilgileri içeren sözlük
            
        Format:
            {
                "id": 1,
                "key": "Kablosuz",
                "question": "Kablosuz kulaklık ister misiniz?",
                "emoji": "🎧"
            }
        """
        question = self.question_tr if language == 'tr' else (self.question_en or self.question_tr)
        return {
            'id': self.id,
            'key': self.key,
            'question': question,
            'emoji': self.emoji
        }

def migrate_from_json():
    """
    JSON dosyasından veritabanına veri aktarımı yapar.
    
    Bu fonksiyon mevcut categories.json dosyasını okur ve
    Category ile CategorySpec tablolarına aktarır.
    
    Returns:
        dict: Migration sonucu raporu
        
    Örnek Dönen Değer:
        {
            "success": True,
            "categories_migrated": 4,
            "specs_migrated": 15,
            "message": "4 kategori ve 15 özellik başarıyla aktarıldı."
        }
    """
    try:
        # JSON dosyasını oku
        with open('categories.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        categories_count = 0
        specs_count = 0
        
        for category_name, category_data in json_data.items():
            # Kategori var mı kontrol et
            existing_category = Category.query.filter_by(name=category_name).first()
            if existing_category:
                print(f"Category {category_name} already exists, skipping...")
                continue
            
            # Yeni kategori oluştur
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()  # ID'yi alabilmek için
            categories_count += 1
            
            # Özellikler varsa ekle
            if 'specs' in category_data:
                for spec_data in category_data['specs']:
                    # Eski format: sadece question var
                    # Yeni format: question_tr ve question_en olacak
                    question_tr = spec_data.get('question', '')
                    question_en = spec_data.get('question_en', None)  # Yoksa None
                    
                    spec = CategorySpec(
                        category_id=category.id,
                        key=spec_data.get('key', ''),
                        question_tr=question_tr,
                        question_en=question_en,
                        emoji=spec_data.get('emoji', '❓')
                    )
                    db.session.add(spec)
                    specs_count += 1
        
        # Değişiklikleri kaydet
        db.session.commit()
        
        # JSON dosyasını yedekle ve sil
        import os
        import shutil
        if os.path.exists('categories.json'):
            shutil.move('categories.json', 'categories.json.backup')
        
        return {
            "success": True,
            "categories_migrated": categories_count,
            "specs_migrated": specs_count,
            "message": f"{categories_count} kategori ve {specs_count} özellik başarıyla aktarıldı."
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": f"Migration sırasında hata oluştu: {str(e)}"
        }
