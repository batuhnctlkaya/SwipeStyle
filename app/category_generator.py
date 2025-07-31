"""
SwipeStyle Akıllı Kategori Üretici Modülü
==========================================

Bu modül, SwipeStyle uygulamasının akıllı kategori tespiti ve oluşturma işlevlerini içerir.
Gemini AI kullanarak kullanıcı sorgularından kategori tespiti yapar ve gerekirse yeni kategoriler oluşturur.

Ana Sınıflar:
- CategoryGenerator: Akıllı kategori tespiti ve oluşturma ana sınıfı

Fonksiyonlar:
- add_dynamic_category_route: Flask uygulamasına dinamik kategori rotaları ekler

Özellikler:
- Akıllı kategori tespiti (exact, partial, AI recognition)
- Yeni kategori oluşturma
- Prompt-chained AI mimarisi
- Confidence scoring
- JSON dosya yönetimi
- Debug log'ları

Gereksinimler:
- Google Generative AI (Gemini)
- categories.json dosyası
- .env dosyasında GEMINI_API_KEY
"""

import json
import os
from .config import setup_gemini, get_gemini_model, generate_with_retry

class CategoryGenerator:
    """
    Akıllı kategori tespiti ve oluşturma sınıfı.
    
    Bu sınıf, kullanıcı sorgularını analiz ederek mevcut kategorilerle eşleştirir
    veya gerekirse yeni kategoriler oluşturur. Prompt-chained AI mimarisi kullanır.
    
    Özellikler:
    - model: Gemini AI modeli
    - categories_file: Kategori dosyası yolu
    - category_cache: Kategori önbelleği
    
    Ana Metodlar:
    - intelligent_category_detection(): Ana kategori tespit metodu
    - _ai_category_recognition(): AI ile kategori tanıma
    - _ai_category_creation(): AI ile yeni kategori oluşturma
    
    Kullanım:
        >>> generator = CategoryGenerator()
        >>> result = generator.intelligent_category_detection("kablosuz kulaklık")
        >>> print(result['category'])
        "Headphones"
    """
    
    def __init__(self):
        """
        CategoryGenerator'ı başlatır ve AI modelini yapılandırır.
        
        Gemini API'yi yapılandırır, kategori dosyası yolunu belirler
        ve kategori önbelleğini başlatır.
        """
        self.model = None
        self.setup_ai()
        self.categories_file = 'categories.json'
        self.category_cache = {}
        
    def setup_ai(self):
        """
        AI modelini başlatır ve yapılandırır.
        
        Gemini API'yi yapılandırır ve model nesnesini oluşturur.
        Hata durumunda model None olarak kalır.
        """
        try:
            setup_gemini()
            self.model = get_gemini_model()
        except Exception as e:
            print(f"AI model setup error: {e}")
            self.model = None
    
    def intelligent_category_detection(self, query):
        """
        Akıllı kategori tespiti ve oluşturma ana metodu.
        
        Bu metod, kullanıcı sorgusunu analiz ederek en uygun kategoriyi tespit eder.
        Önce mevcut kategorilerde eşleşme arar, bulamazsa yeni kategori oluşturur.
        
        Args:
            query (str): Kullanıcı sorgusu (örn: "kablosuz kulaklık")
            
        Returns:
            dict: Tespit sonucu
                - match_type: Eşleşme türü (exact, partial, ai_recognition, ai_created)
                - category: Kategori adı
                - confidence: Güven skoru (0.0-1.0)
                - data: Kategori verileri
                - message: Bilgi mesajı
                
        Örnek:
            >>> result = generator.intelligent_category_detection("apple telefon")
            >>> print(result['category'])
            "Phone"
        """
        query = query.strip().lower()
        print(f"🔍 Starting intelligent category detection for: '{query}'")
        
        # Load existing categories
        categories = self._load_categories()
        
        # Step 1: Direct exact match
        exact_match = self._check_exact_match(query, categories)
        if exact_match:
            return exact_match
            
        # Step 2: Partial/substring match
        partial_match = self._check_partial_match(query, categories)
        if partial_match:
            return partial_match
            
        # Step 3: AI-powered category recognition (existing categories)
        ai_recognition = self._ai_category_recognition(query, categories)
        if ai_recognition['match_type'] != 'no_match':
            return ai_recognition
            
        # Step 4: AI-powered category creation (new categories)
        ai_creation = self._ai_category_creation(query)
        return ai_creation
    
    def _check_exact_match(self, query, categories):
        """
        Mevcut kategorilerde tam eşleşme kontrol eder.
        
        Args:
            query (str): Kullanıcı sorgusu
            categories (dict): Mevcut kategoriler
            
        Returns:
            dict or None: Eşleşme bulunursa sonuç, yoksa None
        """
        if query in categories:
            print(f"✅ Exact match found: '{query}'")
            return {
                "match_type": "exact",
                "category": query,
                "confidence": 1.0,
                "data": categories[query]
            }
        return None
    
    def _check_partial_match(self, query, categories):
        """
        Mevcut kategorilerde kısmi eşleşme kontrol eder.
        
        Args:
            query (str): Kullanıcı sorgusu
            categories (dict): Mevcut kategoriler
            
        Returns:
            dict or None: Eşleşme bulunursa sonuç, yoksa None
        """
        for cat_name in categories:
            if query in cat_name.lower() or cat_name.lower() in query:
                print(f"🔍 Partial match found: '{query}' → '{cat_name}'")
                return {
                    "match_type": "partial",
                    "category": cat_name,
                    "original_query": query,
                    "confidence": 0.8,
                    "data": categories[cat_name]
                }
        return None
    
    def _ai_category_recognition(self, query, categories):
        """
        AI ile mevcut kategorilerde akıllı eşleştirme yapar.
        
        Gemini AI kullanarak kullanıcı sorgusunu mevcut kategorilerle
        semantik olarak eşleştirir.
        
        Args:
            query (str): Kullanıcı sorgusu
            categories (dict): Mevcut kategoriler
            
        Returns:
            dict: AI tanıma sonucu
        """
        if not self.model:
            return {"match_type": "no_match", "category": None, "original": query}
            
        try:
            print(f"🤖 AI category recognition for: '{query}'")
            
            # Create detailed category context
            category_context = self._build_category_context(categories)
            
            # Recognition prompt
            recognition_prompt = f"""
            You are an intelligent category recognition agent. Your task is to map user queries to existing product categories.
            
            USER QUERY: "{query}"
            
            EXISTING CATEGORIES WITH DETAILS:
            {category_context}
            
            RECOGNITION RULES:
            1. Look for semantic similarity between the query and existing categories
            2. Consider synonyms, abbreviations, and alternative names
            3. Consider language variations (English/Turkish)
            4. Examples:
               - "pc" should map to "bilgisayar" or "computer"
               - "apple telefon" should map to "phone" or "telefon"
               - "ac" should map to "klima" (air conditioner)
               - "şarj aleti" should map to relevant charging category
            
            RESPONSE FORMAT:
            If you find a match, respond with ONLY the exact category name from the list.
            If no match exists, respond with "NO_MATCH".
            
            CATEGORY NAME OR NO_MATCH:
            """
            
            response = generate_with_retry(self.model, recognition_prompt, max_retries=2, delay=2)
            suggested_category = response.text.strip()
            
            print(f"🤖 AI recognition result: '{query}' → '{suggested_category}'")
            
            # Validate the suggestion
            if suggested_category != "NO_MATCH" and suggested_category in categories:
                # Confidence validation
                confidence = self._validate_recognition_confidence(query, suggested_category)
                
                if confidence >= 0.6:  # Minimum confidence threshold
                    return {
                        "match_type": "ai_recognition",
                        "category": suggested_category,
                        "original_query": query,
                        "confidence": confidence,
                        "data": categories[suggested_category]
                    }
                else:
                    print(f"⚠️ Low confidence score: {confidence}, proceeding to creation")
            
        except Exception as e:
            print(f"❌ AI recognition error: {e}")
            
        return {"match_type": "no_match", "category": None, "original": query}
    
    def _validate_recognition_confidence(self, query, suggested_category):
        """
        AI tanıma sonucunun güven skorunu doğrular.
        
        Args:
            query (str): Orijinal kullanıcı sorgusu
            suggested_category (str): AI'nın önerdiği kategori
            
        Returns:
            float: Güven skoru (0.0-1.0)
        """
        try:
            validation_prompt = f"""
            Rate the accuracy of this category mapping on a scale of 0.0 to 1.0:
            
            User searched for: "{query}"
            Mapped to category: "{suggested_category}"
            
            Consider:
            - Semantic similarity
            - Language appropriateness
            - Logical connection
            
            Respond with ONLY a decimal number between 0.0 and 1.0:
            """
            
            response = generate_with_retry(self.model, validation_prompt, max_retries=2, delay=1)
            confidence = float(response.text.strip())
            return min(max(confidence, 0.0), 1.0)  # Clamp between 0-1
            
        except:
            return 0.5  # Default confidence if validation fails
    
    def _ai_category_creation(self, query):
        """
        AI ile yeni kategori oluşturur.
        
        Mevcut kategorilerde eşleşme bulunamadığında, Gemini AI
        kullanarak yeni kategori oluşturur ve categories.json'a kaydeder.
        
        Args:
            query (str): Kullanıcı sorgusu
            
        Returns:
            dict: Kategori oluşturma sonucu
        """
        if not self.model:
            return {"match_type": "error", "message": "AI model not available"}
            
        try:
            print(f"🆕 AI category creation for: '{query}'")
            
            # Determine the appropriate category name
            category_name = self._determine_category_name(query)
            
            # Generate category specifications
            category_data = self._generate_category_specs(category_name)
            
            if category_data:
                # Save the new category
                self._save_new_category(category_name, category_data)
                
                return {
                    "match_type": "ai_created",
                    "category": category_name,
                    "original_query": query,
                    "confidence": 0.9,
                    "data": category_data,
                    "message": f"New category '{category_name}' created successfully"
                }
            else:
                return {"match_type": "creation_failed", "message": "Failed to create category"}
                
        except Exception as e:
            print(f"❌ AI category creation error: {e}")
            return {"match_type": "error", "message": f"Category creation failed: {str(e)}"}
    
    def _determine_category_name(self, query):
        """
        Sorgu için uygun kategori adını belirler.
        
        Args:
            query (str): Kullanıcı sorgusu
            
        Returns:
            str: Belirlenen kategori adı
        """
        try:
            naming_prompt = f"""
            You are a category naming expert. Given a user query, determine the best category name.
            
            USER QUERY: "{query}"
            
            NAMING RULES:
            1. Use clear, general category names (not specific product names)
            2. Prefer English names for consistency
            3. Use singular form
            4. Examples:
               - "apple telefon" → "Phone"
               - "samsung laptop" → "Laptop"
               - "gaming mouse" → "Mouse"
               - "bluetooth kulaklık" → "Headphones"
               - "klima" → "Klima" (keep Turkish for local products)
            
            Respond with ONLY the category name (1-2 words maximum):
            """
            
            response = generate_with_retry(self.model, naming_prompt, max_retries=2, delay=1)
            category_name = response.text.strip().title()
            
            # Sanitize the name
            category_name = ''.join(c for c in category_name if c.isalnum() or c.isspace()).strip()
            
            return category_name if category_name else query.title()
            
        except:
            return query.title()
    
    def _generate_category_specs(self, category_name):
        """
        AI kullanarak kategori özelliklerini oluşturur.
        
        Args:
            category_name (str): Kategori adı
            
        Returns:
            dict or None: Oluşturulan kategori özellikleri
        """
        try:
            # Load existing categories for examples
            categories = self._load_categories()
            examples = self._get_category_examples(categories)
            
            generation_prompt = f"""
            Generate a complete category specification for "{category_name}" following the exact format of existing categories.
            
            EXISTING CATEGORY EXAMPLES:
            {examples}
            
            REQUIREMENTS:
            1. Create "budget_bands" with 5 price ranges in both TR and EN
            2. Create "specs" array with 3-5 relevant specifications
            3. Each spec must have: id, type, label (tr/en), emoji, tooltip (tr/en), weight
            4. Types: "single_choice", "boolean", "number"
            5. For single_choice, include "options" array with id and label (tr/en)
            6. Make it relevant to "{category_name}" products
            7. Use appropriate Turkish and English translations
            
            OUTPUT ONLY VALID JSON (no markdown, no explanations):
            """
            
            print(f"🤖 Yeni kategori oluşturuluyor: {category_name} (Bu işlem 15-45 saniye sürebilir)")
            response = generate_with_retry(self.model, generation_prompt, max_retries=3, delay=3)
            return self._parse_ai_response(response.text, category_name)
            
        except Exception as e:
            print(f"❌ Category spec generation error: {e}")
            return self._get_default_template(category_name)
    
    def _build_category_context(self, categories):
        """
        Mevcut kategoriler için detaylı bağlam oluşturur.
        
        Args:
            categories (dict): Mevcut kategoriler
            
        Returns:
            str: Kategori bağlam metni
        """
        context_parts = []
        
        for cat_name, cat_data in categories.items():
            # Extract key characteristics
            specs_summary = []
            if "specs" in cat_data:
                for spec in cat_data["specs"][:3]:  # First 3 specs
                    if "label" in spec and "tr" in spec["label"]:
                        specs_summary.append(spec["label"]["tr"])
            
            # Build context entry
            context_entry = f"- {cat_name}: {', '.join(specs_summary) if specs_summary else 'General product'}"
            context_parts.append(context_entry)
        
        return '\n'.join(context_parts)
    
    def _get_category_examples(self, categories):
        """
        AI oluşturma için kategori örnekleri alır.
        
        Args:
            categories (dict): Mevcut kategoriler
            
        Returns:
            str: Kategori örnekleri JSON formatında
        """
        examples = []
        for cat_name, cat_data in list(categories.items())[:2]:  # First 2 categories
            examples.append(f'"{cat_name}": {json.dumps(cat_data, indent=2, ensure_ascii=False)}')
        
        return '\n\n'.join(examples)
    
    def _parse_ai_response(self, text, category_name):
        """
        AI yanıtını kategori verilerine dönüştürür.
        
        Args:
            text (str): AI'dan gelen ham yanıt
            category_name (str): Kategori adı
            
        Returns:
            dict or None: Ayrıştırılmış kategori verileri
        """
        try:
            # Clean the response
            json_content = text.strip()
            if json_content.startswith('```json'):
                json_content = json_content[7:]
            if json_content.endswith('```'):
                json_content = json_content[:-3]
            
            # Parse JSON
            parsed = json.loads(json_content)
            
            # Validate structure
            if isinstance(parsed, dict) and "budget_bands" in parsed and "specs" in parsed:
                return parsed
            elif category_name in parsed:
                return parsed[category_name]
            
            print(f"Unexpected AI response format")
            return None
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return None
    
    def _load_categories(self):
        """
        Mevcut kategorileri yükler.
        
        Returns:
            dict: Yüklenen kategoriler
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(current_dir)
            categories_path = os.path.join(root_dir, self.categories_file)
            
            with open(categories_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_new_category(self, category_name, category_data):
        """
        Yeni kategoriyi categories.json dosyasına kaydeder.
        
        Args:
            category_name (str): Kategori adı
            category_data (dict): Kategori verileri
            
        Returns:
            bool: Kaydetme başarılı mı?
        """
        try:
            categories = self._load_categories()
            categories[category_name] = category_data
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(current_dir)
            categories_path = os.path.join(root_dir, self.categories_file)
            
            with open(categories_path, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Category '{category_name}' saved successfully")
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def _get_default_template(self, category_name):
        """
        AI oluşturma başarısız olduğunda varsayılan şablon döner.
        
        Args:
            category_name (str): Kategori adı
            
        Returns:
            dict: Varsayılan kategori şablonu
        """
        return {
            "budget_bands": {
                "tr": ["1-3k₺", "3-6k₺", "6-12k₺", "12-20k₺", "20k₺+"],
                "en": ["$30-100", "$100-200", "$200-400", "$400-600", "$600+"]
            },
            "specs": [
                {
                    "id": "quality",
                    "type": "single_choice",
                    "label": {"tr": f"{category_name} kalitesi?", "en": f"{category_name} quality?"},
                    "emoji": "⭐",
                    "tooltip": {
                        "tr": f"{category_name} için kalite seviyenizi seçin.",
                        "en": f"Choose quality level for your {category_name}."
                    },
                    "options": [
                        {"id": "basic", "label": {"tr": "Temel", "en": "Basic"}},
                        {"id": "standard", "label": {"tr": "Standart", "en": "Standard"}},
                        {"id": "premium", "label": {"tr": "Premium", "en": "Premium"}},
                        {"id": "no_preference", "label": {"tr": "Fark etmez", "en": "No preference"}}
                    ],
                    "weight": 1.0
                },
                {
                    "id": "brand_importance",
                    "type": "boolean",
                    "label": {"tr": "Marka önemli mi?", "en": "Is brand important?"},
                    "emoji": "🏷️",
                    "tooltip": {
                        "tr": "Ürün seçiminde marka önemli bir faktör mü?",
                        "en": "Is brand an important factor in product selection?"
                    },
                    "weight": 0.7
                }
            ]
        }

# Flask route integration
def add_dynamic_category_route(app):
    """
    Flask uygulamasına dinamik kategori rotaları ekler.
    
    Bu fonksiyon, Flask uygulamasına akıllı kategori tespiti
    için gerekli endpoint'leri ekler.
    
    Args:
        app: Flask uygulama nesnesi
        
    Returns:
        None: Rota'lar uygulamaya eklenir
        
    Örnek:
        >>> from flask import Flask
        >>> app = Flask(__name__)
        >>> add_dynamic_category_route(app)
        >>> # /search/<query> endpoint'i artık mevcut
    """
    category_generator = CategoryGenerator()
    
    @app.route('/search/<query>', methods=['GET'])
    def search_category(query):
        """
        Akıllı kategori tespiti için ana arama endpoint'i.
        
        Bu endpoint, kullanıcı sorgusunu alır ve akıllı kategori
        tespiti yapar. Mevcut kategorilerde eşleşme arar veya
        yeni kategori oluşturur.
        
        Args:
            query (str): Kullanıcı arama sorgusu
            
        Returns:
            dict: Tespit sonucu JSON formatında
        """
        try:
            print(f"🔍 Search request for: '{query}'")
            
            # Use intelligent category detection
            result = category_generator.intelligent_category_detection(query)
            
            # Format response based on match type
            if result['match_type'] in ['exact', 'partial', 'ai_recognition']:
                return {
                    "status": "found",
                    "match_type": result['match_type'],
                    "category": result['category'],
                    "original_query": result.get('original_query', query),
                    "confidence": result.get('confidence', 1.0),
                    "message": f"'{query}' mapped to '{result['category']}'",
                    "data": result['data']
                }
            elif result['match_type'] == 'ai_created':
                return {
                    "status": "created",
                    "category": result['category'],
                    "original_query": result.get('original_query', query),
                    "confidence": result.get('confidence', 0.9),
                    "message": result.get('message', f"New category '{result['category']}' created"),
                    "data": result['data']
                }
            else:
                return {
                    "status": "error",
                    "message": result.get('message', 'Category detection failed')
                }, 500
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {"status": "error", "message": str(e)}, 500
