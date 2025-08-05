"""
SwipeStyle Agent Modülü

Bu modül, kullanıcı etkileşimlerini yöneten, dinamik soru-cevap akışını kontrol eden
ve AI destekli ürün önerileri oluşturan ana agent sınıfını içerir.

Ana Özellikler:
- Akıllı kategori tespiti (prompt-chained agent mimarisi)
- Dinamik soru-cevap akışı
- Tercih analizi ve güven skoru hesaplama
- AI destekli ürün önerileri (Gemini entegrasyonu)
- Çok dilli destek (Türkçe/İngilizce)
- Bütçe yönetimi
- Bağımlılık tabanlı akış kontrolü

Ana Sınıflar:
- Agent: Ana agent sınıfı, kullanıcı etkileşimlerini yönetir

Ana Fonksiyonlar:
- detect_category_from_query(): Gelişmiş kategori tespiti
- Agent.handle(): Ana işlem fonksiyonu
- Agent._generate_recommendations(): AI öneri oluşturma

Gereksinimler:
- categories.json dosyası
- Gemini API anahtarı
- Flask framework

Kullanım:
    from app.agent import Agent, detect_category_from_query
    
    # Kategori tespiti
    category = detect_category_from_query("telefon")
    
    # Agent kullanımı
    agent = Agent()
    response = agent.handle({
        'step': 0,
        'category': 'Phone',
        'answers': ['Yes', 'No'],
        'language': 'tr'
    })
"""

import json
import os
from datetime import datetime
from .config import setup_gemini, get_gemini_model, generate_with_retry
import json

def log_category_detection(query, result, method="direct"):
    """
    Kategori tespit sonuçlarını loglar
    
    Args:
        query (str): Kullanıcı sorgusu
        result (str): Tespit edilen kategori
        method (str): Tespit yöntemi
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open('agent_output_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n🔍 [{timestamp}] CATEGORY DETECTION\n")
            f.write(f"Query: '{query}'\n")
            f.write(f"Result: '{result}'\n")
            f.write(f"Method: {method}\n")
            f.write(f"-"*40 + "\n")
            
    except Exception as e:
        print(f"❌ Category detection logging error: {e}")

def detect_category_from_query(query):
    """
    Gelişmiş kategori tespiti - prompt-chained agent mimarisi kullanarak
    
    Bu fonksiyon, kullanıcı sorgusunu analiz ederek en uygun ürün kategorisini
    tespit eder. Hem yerel eşleştirme hem de AI destekli tanıma kullanır.
    
    Args:
        query (str): Kullanıcının arama sorgusu (örn: "telefon", "kulaklık")
        
    Returns:
        str or None: Tespit edilen kategori adı veya None (bulunamazsa)
        
    Özellikler:
        - Yerel Türkçe-İngilizce eşleştirme
        - AI destekli kategori tanıma
        - Yeni kategori oluşturma
        - Hata yönetimi ve loglama
        
    Örnek:
        >>> detect_category_from_query("telefon")
        'Phone'
        >>> detect_category_from_query("kulaklık")
        'Headphones'
        >>> detect_category_from_query("bilinmeyen ürün")
        'NewCategory'  # AI tarafından oluşturulur
    """
    try:
        print(f"🔍 Detecting category for query: '{query}'")
        
        # Quick local mapping for common Turkish terms
        # Only include categories that actually exist in categories.json
        local_mappings = {
            'kulaklık': 'Headphones',
            'kulaklik': 'Headphones',
            'headphones': 'Headphones',
            'telefon': 'Phone',
            'phone': 'Phone',
            'laptop': 'Laptop',
            'dizüstü': 'Laptop',
            'bilgisayar': 'Laptop',
            'computer': 'Laptop',
            'pc': 'Laptop',
            'mouse': 'Mouse',
            'fare': 'Mouse',
            # Removed non-existing categories: Charger, Klima, Drill, Hair Dryer
            # These will be handled by CategoryGenerator AI creation
        }
        
        query_lower = query.strip().lower()
        
        # Check local mappings first
        if query_lower in local_mappings:
            mapped_category = local_mappings[query_lower]
            print(f"✅ Local mapping found: '{query}' → '{mapped_category}'")
            log_category_detection(query, mapped_category, "local_mapping")
            return mapped_category
        
        from .category_generator import CategoryGenerator
        
        # Use the new intelligent category detection system
        category_generator = CategoryGenerator()
        result = category_generator.intelligent_category_detection(query)
        
        # Handle different match types
        if result['match_type'] in ['exact', 'partial', 'ai_recognition']:
            print(f"✅ Category found: {result['match_type']} - '{result['category']}'")
            log_category_detection(query, result['category'], result['match_type'])
            return result['category']
            
        elif result['match_type'] == 'ai_created':
            print(f"🆕 New category created: '{result['category']}'")
            log_category_detection(query, result['category'], "ai_created")
            return result['category']
            
        else:
            print(f"❌ Category detection failed: {result.get('message', 'Unknown error')}")
            log_category_detection(query, None, "failed")
            # Return None instead of defaulting to prevent confusion
            return None
            
    except Exception as e:
        print(f"❌ Category detection error: {e}")
        import traceback
        print(traceback.format_exc())
        log_category_detection(query, None, f"error: {str(e)}")
        return None

class Agent:
    """
    Ana Agent Sınıfı - Dinamik Soru-Cevap ve AI Öneri Sistemi
    
    Bu sınıf, kullanıcı etkileşimlerini yöneten, dinamik soru-cevap akışını
    kontrol eden ve AI destekli ürün önerileri oluşturan ana agent'tır.
    
    Ana Özellikler:
        - Dinamik soru-cevap akışı
        - Tercih analizi ve güven skoru hesaplama
        - AI destekli ürün önerileri (Gemini entegrasyonu)
        - Çok dilli destek (Türkçe/İngilizce)
        - Bütçe yönetimi ve kategori-spesifik aralıklar
        - Bağımlılık tabanlı akış kontrolü
        - Akıllı follow-up soru belirleme
        
    Ana Metodlar:
        - handle(): Ana işlem fonksiyonu
        - _generate_recommendations(): AI öneri oluşturma
        - _determine_next_followup(): Sonraki soru belirleme
        - _analyze_current_preferences(): Tercih analizi
        
    Kullanım:
        agent = Agent()
        response = agent.handle({
            'step': 0,
            'category': 'Phone',
            'answers': ['Yes', 'No'],
            'language': 'tr'
        })
    """
    
    def __init__(self):
        self.categories = self.load_categories()

    def log_agent_output(self, output_type, data, input_data=None):
        """
        Agent'ın ürettiği çıktıları ayrı bir dosyaya loglar
        
        Args:
            output_type (str): Çıktı tipi (question, recommendations, error, etc.)
            data (dict): Agent'ın döndürdüğü veri
            input_data (dict): Agent'a gönderilen input verisi (opsiyonel)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open('agent_output_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"⏰ [{timestamp}] Agent Output Type: {output_type}\n")
                f.write(f"{'='*80}\n")
                
                if input_data:
                    f.write(f"📥 INPUT DATA:\n")
                    f.write(f"{json.dumps(input_data, indent=2, ensure_ascii=False)}\n")
                    f.write(f"-"*40 + "\n")
                
                f.write(f"📤 OUTPUT DATA:\n")
                f.write(f"{json.dumps(data, indent=2, ensure_ascii=False)}\n")
                f.write(f"\n")
                
        except Exception as e:
            print(f"❌ Logging error: {e}")

    def load_categories(self):
        try:
            with open('categories.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ categories.json dosyası bulunamadı!")
            return {}

    def handle(self, data):
        # Auto-reload categories to pick up manual edits
        self.categories = self.load_categories()
        step = data.get('step', 0)
        category = data.get('category', '')
        answers = data.get('answers', [])
        language = data.get('language', 'en')
        
        print(f"🔄 Agent.handle çağrıldı - Step: {step}, Category: {category}, Answers: {answers}")
        print(f"📊 Raw data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Initialize response variable
        response = None
        
        if step == 0:
            # İlk adım: Kategori seçimi
            response = {
                'question': 'What tech are you shopping for?' if language == 'en' else 'Hangi teknoloji ürününü arıyorsunuz?',
                'categories': list(self.categories.keys())
            }
            # Log the response
            self.log_agent_output("category_selection", response, data)
            return response
        
        elif category and category in self.categories:
            specs = self.categories[category]['specs']
            
            # Frontend'den gelen asked_spec_ids bilgisini al
            asked_spec_ids = data.get('asked_spec_ids', [])
            
            # Kullanıcının mevcut tercihlerini analiz et
            preferences = self._analyze_current_preferences(answers, specs, asked_spec_ids)
            
            # Frontend'den gelen özel alanları ekle (budget_band gibi)
            if 'budget_band' in data:
                preferences['budget_band'] = data['budget_band']
            
            confidence_score = self._calculate_confidence_score(preferences, specs)
            
            print(f"🎯 Preferences: {json.dumps(preferences, indent=2, ensure_ascii=False)}")
            print(f"📈 Confidence Score: {confidence_score}")
            
            # Akıllı follow-up soru belirleme
            next_question = self._determine_next_followup(specs, preferences, confidence_score, language, category)
            
            if next_question:
                # Progress bilgisi ekle
                progress = self._calculate_progress(preferences, specs)
                next_question['progress'] = progress
                # Log the question response
                self.log_agent_output("follow_up_question", next_question, data)
                return next_question
            else:
                # Tüm gerekli bilgiler toplandı, öneri ver
                response = self._generate_recommendations(category, preferences, specs, language)
                # Log the recommendations response
                self.log_agent_output("recommendations", response, data)
                return response
        
        else:
            print(f"❌ Invalid category or step!")
            print(f"   Step: {step}")
            print(f"   Category: '{category}'")
            print(f"   Category exists in self.categories: {category in self.categories if category else 'N/A'}")
            print(f"   Available categories: {list(self.categories.keys())}")
            response = {'error': 'Invalid category or step'}
            # Log the error response
            self.log_agent_output("error", response, data)
            return response

    def _analyze_current_preferences(self, answers, specs, asked_spec_ids=None):
        """Mevcut cevapları tercih objesi haline getir - doğru spec'e eşleştirme ile"""
        preferences = {}
        
        print(f"🔍 _analyze_current_preferences:")
        print(f"  📊 answers_count={len(answers)}")
        print(f"  📋 specs_count={len(specs)}")
        print(f"  📝 answers={answers}")
        print(f"  🎯 asked_spec_ids={asked_spec_ids}")
        # Fix the budget_band issue by ensuring proper formatting of spec IDs
        print(f"  🏷️ spec_ids=[{', '.join([spec['id'].strip() for spec in specs])}]")
        
        # ✅ YENİ YÖNTEM: asked_spec_ids varsa bunları kullan
        if asked_spec_ids and len(asked_spec_ids) == len(answers):
            print(f"  ✅ Using asked_spec_ids for precise matching")
            
            # Create spec lookup dictionary
            spec_lookup = {spec['id']: spec for spec in specs}
            
            for i, (answer, spec_id) in enumerate(zip(answers, asked_spec_ids)):
                if answer is not None and spec_id in spec_lookup:
                    spec = spec_lookup[spec_id]
                    print(f"  📋 Processing answer {i}: {spec_id} = '{answer}' (type: {spec['type']})")
                    
                    if spec['type'] == 'boolean':
                        if answer.lower() in ['yes', 'evet', 'true']:
                            preferences[spec_id] = True
                            print(f"    ✅ Boolean value: True")
                        elif answer.lower() in ['no', 'hayır', 'false']:
                            preferences[spec_id] = False
                            print(f"    ✅ Boolean value: False")
                        elif answer.lower() in ['no preference', 'fark etmez', 'bilmiyorum', 'farketmez']:
                            preferences[spec_id] = None  # No preference
                            print(f"    ✅ Boolean value: No preference (None)")
                        else:
                            print(f"    ❌ Invalid boolean answer: '{answer}'")
                    elif spec['type'] == 'single_choice':
                        # Seçilen option'ın ID'sini bul
                        option_found = False
                        for opt in spec['options']:
                            if opt['label']['en'] == answer or opt['label']['tr'] == answer:
                                preferences[spec_id] = opt['id']
                                option_found = True
                                print(f"    ✅ Mapped to option_id: {opt['id']}")
                                break
                        if not option_found:
                            print(f"    ❌ No option found for answer: '{answer}'")
                    elif spec['type'] == 'number':
                        try:
                            preferences[spec_id] = int(answer)
                            print(f"    ✅ Converted to number: {int(answer)}")
                        except ValueError:
                            preferences[spec_id] = None
                            print(f"    ❌ Could not convert to number: '{answer}'")
        else:
            # ❌ ESKİ YÖNTEM: Fallback olarak indeks bazlı eşleştirme (eski kategoriler için)
            print(f"  ⚠️ Falling back to index-based matching (old method)")
            
            # answered_specs - sadece cevaplanan spec'leri işle
            for i, answer in enumerate(answers):
                if i < len(specs) and answer is not None:
                    spec = specs[i]
                    spec_id = spec['id']
                    
                    print(f"  📋 Processing spec {i}: {spec_id} = '{answer}' (type: {spec['type']})")
                    
                    if spec['type'] == 'boolean':
                        if answer.lower() in ['yes', 'evet', 'true']:
                            preferences[spec_id] = True
                            print(f"    ✅ Boolean value: True")
                        elif answer.lower() in ['no', 'hayır', 'false']:
                            preferences[spec_id] = False
                            print(f"    ✅ Boolean value: False")
                        elif answer.lower() in ['no preference', 'fark etmez', 'bilmiyorum', 'farketmez']:
                            preferences[spec_id] = None  # No preference
                            print(f"    ✅ Boolean value: No preference (None)")
                        else:
                            print(f"    ❌ Invalid boolean answer: '{answer}'")
                    elif spec['type'] == 'single_choice':
                        # Seçilen option'ın ID'sini bul
                        option_found = False
                        for opt in spec['options']:
                            if opt['label']['en'] == answer or opt['label']['tr'] == answer:
                                preferences[spec_id] = opt['id']
                                option_found = True
                                print(f"    ✅ Mapped to option_id: {opt['id']}")
                                break
                        if not option_found:
                            print(f"    ❌ No option found for answer: '{answer}'")
                    elif spec['type'] == 'number':
                        try:
                            preferences[spec_id] = int(answer)
                            print(f"    ✅ Converted to number: {int(answer)}")
                        except ValueError:
                            preferences[spec_id] = None
                            print(f"    ❌ Could not convert to number: '{answer}'")
        
        # Özel bütçe kontrolü - Para birimi sembolü içeren yanıtları bütçe olarak tanı
        for i, answer in enumerate(answers):
            if answer and ('$' in answer or '₺' in answer):
                preferences['budget_band'] = answer
                print(f"  💰 Special budget detection: '{answer}' added as budget_band")
                
                # Eğer bu cevap bir spec'e eşleştirildiyse temizle
                if asked_spec_ids and i < len(asked_spec_ids):
                    spec_id = asked_spec_ids[i]
                    if spec_id in preferences and spec_id != 'budget_band':
                        preferences[spec_id] = None
                        print(f"  ⚠️ Clearing {spec_id} since this was actually a budget answer")
        
        print(f"  🎯 Final preferences: {json.dumps(preferences, indent=2, ensure_ascii=False)}")
        return preferences

    def _has_unsatisfied_dependencies(self, spec, preferences):
        """Spec'in dependency'leri sağlanmıyor mu kontrol et"""
        if 'depends_on' not in spec:
            print(f"  👍 No dependencies for {spec['id']}")
            return False
            
        print(f"  🔍 Checking dependencies for {spec['id']}: {spec.get('depends_on')}")
        
        for dep in spec['depends_on']:
            dep_id = dep['id']
            expected_value = dep['eq']
            
            if dep_id not in preferences:
                print(f"  ❌ Dependency {dep_id} not answered")
                return True  # Dependency cevaplanmamış
                
            actual_value = preferences[dep_id]
            print(f"  ⚙️ Dependency check: {dep_id}={actual_value}, expected={expected_value}")
            
            # No preference varsa dependency sağlanmıyor
            if actual_value == "no_preference" or actual_value is None:
                print(f"  ❌ Dependency value is 'no_preference' or None")
                return True
                
            # String/bool karşılaştırma için fix
            if isinstance(expected_value, bool) and isinstance(actual_value, str):
                # String to boolean conversion
                if actual_value.lower() in ['true', 'yes', 'evet']:
                    actual_value = True
                elif actual_value.lower() in ['false', 'no', 'hayır']:
                    actual_value = False
            
            if actual_value != expected_value:
                print(f"  ❌ Dependency value doesn't match: {actual_value} != {expected_value}")
                return True  # Dependency sağlanmıyor
        
        print(f"  ✅ All dependencies satisfied for {spec['id']}")
        return False  # Tüm dependency'ler sağlanıyor

    def _calculate_confidence_score(self, preferences, specs):
        """Toplam güven skorunu hesapla (weight'lere göre)"""
        total_weight = sum(spec.get('weight', 1.0) for spec in specs)
        answered_weight = sum(
            spec.get('weight', 1.0) 
            for spec in specs 
            if spec['id'] in preferences  # None da valid bir cevap sayılır
        )
        
        return answered_weight / total_weight if total_weight > 0 else 0

    def _calculate_progress(self, preferences, specs):
        """İlerleme yüzdesini hesapla"""
        answered_count = len([spec_id for spec_id in [spec['id'] for spec in specs] if spec_id in preferences])
        total_count = len(specs)
        return int((answered_count / total_count) * 100) if total_count > 0 else 0

    def _determine_next_followup(self, specs, preferences, confidence_score, language, category=None):
        """Akıllı follow-up soru belirleme algoritması"""
        
        # 1) Çelişki var mı kontrol et
        conflict_question = self._check_conflicts(specs, preferences, language)
        if conflict_question:
            return conflict_question
        
        # 2) Zorunlu/önemli eksikler (mandatory veya weight ≥ 0.9)
        mandatory_question = self._check_mandatory_missing(specs, preferences, language)
        if mandatory_question:
            return mandatory_question
        
        # 3) depends_on tetiklenen alt sorular
        dependency_question = self._check_dependency_triggers(specs, preferences, language)
        if dependency_question:
            return dependency_question
        
        # 4) Yüksek weight'li eksikler - confidence'tan bağımsız kontrol et
        # Makul weight'e sahip (>=0.6) eksik spec'ler varsa onları sor
        high_weight_question = self._check_high_weight_missing_improved(specs, preferences, language)
        if high_weight_question:
            return high_weight_question
        
        # 5) Sayısal detay gereken sorular
        numeric_question = self._check_numeric_needed(specs, preferences, language)
        if numeric_question:
            return numeric_question
        
        # 6) Bütçe sor (eğer yoksa) - kategori bilgisi ile
        budget_question = self._check_budget_needed(preferences, language, category)
        if budget_question:
            return budget_question
        
        return None  # Artık öneriye geç
    """
    BURAYA TEKRAR BAKALIM
    """
    def _check_conflicts(self, specs, preferences, language):
        """Çelişki kontrolü"""
        # Örnek: aynı kategoride farklı seçimler
        # Bu basit örnek, daha karmaşık çelişki mantığı eklenebilir
        return None

    def _check_mandatory_missing(self, specs, preferences, language):
        """Zorunlu veya çok önemli (weight≥0.9) eksik sorular"""
        missing = [
            spec for spec in specs 
            if (spec.get('weight', 1.0) >= 0.9 or spec.get('mandatory', False)) 
            and spec['id'] not in preferences
            and not self._has_unsatisfied_dependencies(spec, preferences)  # Dependency'si olmayan veya sağlanan sorular
        ]
        
        print(f"  🎯 Mandatory check: found {len(missing)} missing mandatory specs")
        
        if missing:
            return self._format_question(missing[0], language, reason="mandatory")
        return None

    def _check_dependency_triggers(self, specs, preferences, language):
        """Bağımlılık tetikleyen sorular"""
        for spec in specs:
            if spec['id'] not in preferences and 'depends_on' in spec:
                # Dependency koşulları sağlanıyor mu?
                should_ask = True
                for dep in spec['depends_on']:
                    dep_id = dep['id']
                    expected_value = dep['eq']
                    
                    if dep_id not in preferences:
                        should_ask = False
                        break
                    
                    actual_value = preferences[dep_id]
                    
                    # No preference varsa dependency'yi atla
                    if actual_value == "no_preference" or actual_value is None:
                        should_ask = False
                        break
                        
                    if actual_value != expected_value:
                        should_ask = False
                        break
                
                if should_ask:
                    print(f"  🔗 Dependency triggered for {spec['id']}: {spec['depends_on']}")
                    return self._format_question(spec, language, reason="dependency")
        
        return None

    def _check_high_weight_missing_improved(self, specs, preferences, language):
        """Geliştirilmiş yüksek önemde eksik soru kontrolü - confidence'tan bağımsız"""
        
        # Önce ağırlıklı (>=0.6) eksik spec'leri ara
        missing_high = [
            spec for spec in specs 
            if spec.get('weight', 1.0) >= 0.6 
            and spec['id'] not in preferences
            and not self._has_unsatisfied_dependencies(spec, preferences)
        ]
        
        # Eğer yüksek ağırlıklı bulunamazsa, herhangi bir eksik spec'i ara (>=0.5)
        if not missing_high:
            missing_high = [
                spec for spec in specs 
                if spec.get('weight', 1.0) >= 0.5 
                and spec['id'] not in preferences
                and not self._has_unsatisfied_dependencies(spec, preferences)
            ]
        
        # Hala bulunamazsa, herhangi bir eksik spec'i ara (threshold yok)
        if not missing_high:
            missing_high = [
                spec for spec in specs 
                if spec['id'] not in preferences
                and not self._has_unsatisfied_dependencies(spec, preferences)
            ]
        
        print(f"  📈 Improved high weight check: found {len(missing_high)} missing specs")
        
        # En yüksek weight'li olanı seç
        if missing_high:
            missing_high.sort(key=lambda x: x.get('weight', 1.0), reverse=True)
            selected_spec = missing_high[0]
            print(f"    🎯 Will ask: {selected_spec['id']} (weight: {selected_spec.get('weight', 1.0)})")
            return self._format_question(selected_spec, language, reason="importance")
        return None

    def _check_high_weight_missing(self, specs, preferences, language):
        """Yüksek önemde ama henüz cevaplanmamış sorular"""
        
        # Budget sorulduysa weight threshold'u daha yüksek yap (sadece çok kritik olanlar)
        threshold = 0.9 if 'budget_band' in preferences else 0.6
        
        missing = [
            spec for spec in specs 
            if spec.get('weight', 1.0) >= threshold 
            and spec['id'] not in preferences
            and not self._has_unsatisfied_dependencies(spec, preferences)  # Dependency'si sağlanan sorular
        ]
        
        print(f"  📈 High weight check: threshold={threshold}, missing_count={len(missing)}")
        
        # En yüksek weight'li olanı seç
        if missing:
            missing.sort(key=lambda x: x.get('weight', 1.0), reverse=True)
            print(f"    🎯 Will ask: {missing[0]['id']} (weight: {missing[0].get('weight', 1.0)})")
            return self._format_question(missing[0], language, reason="importance")
        return None

    def _check_numeric_needed(self, specs, preferences, language):
        """Sayısal detay gereken sorular"""
        
        # Budget sorulduysa sayısal soruları atla (çok kritik olanlar hariç)
        if 'budget_band' in preferences:
            print(f"  🔢 Numeric check: Budget exists, skipping numeric questions")
            return None
            
        numeric_missing = [
            spec for spec in specs 
            if spec['type'] == 'number' 
            and spec['id'] not in preferences
            and not self._has_unsatisfied_dependencies(spec, preferences)  # BU SATIR EKLENDİ
        ]
        
        print(f"  🔢 Numeric check: found {len(numeric_missing)} missing numeric specs")
        
        if numeric_missing:
            return self._format_question(numeric_missing[0], language, reason="quantification")
        return None

    def _check_budget_needed(self, preferences, language, category=None):
        """Bütçe bilgisi gerekli mi? - Kategori-spesifik bütçe aralıkları"""
        print(f"💰 _check_budget_needed: budget_band in preferences? {'budget_band' in preferences}")
        
        if 'budget_band' in preferences:
            print(f"  ✅ Budget already set: {preferences['budget_band']}")
            return None
        
        print(f"  ❌ Budget missing, will ask for it")
        
        # Kategori-spesifik bütçe aralıkları
        budget_ranges = self._get_category_budget_ranges(category, language)
        
        # Ensure ID is always correctly formatted without spaces
        return {
            'id': 'budget_band', # Consistent ID without spaces
            'type': 'single_choice',
            'question': 'What\'s your budget range?' if language == 'en' else 'Bütçe aralığın nedir?',
            'emoji': '💰',
            'options': budget_ranges,
            'reason': 'budget',
            'tooltip': 'This helps me recommend products in your price range' if language == 'en' 
                      else 'Bu, fiyat aralığınıza uygun ürünler önermeme yardımcı olur'
        }

    def _get_category_budget_ranges(self, category, language):
        """Kategori-spesifik bütçe aralıklarını döndür"""
        
        if category and category in self.categories:
            # categories.json'dan direkt olarak al
            if "budget_bands" in self.categories[category]:
                return self.categories[category]["budget_bands"].get(language, 
                       self.categories[category]["budget_bands"]["en"])
        
        # Fallback: Genel elektronik bütçesi
        default_budgets = {
            'tr': ['1-3k₺', '3-7k₺', '7-15k₺', '15-30k₺', '30k₺+'],
            'en': ['$30-100', '$100-200', '$200-500', '$500-1000', '$1000+']
        }
        
        return default_budgets.get(language, default_budgets["en"])

    def _should_show_spec(self, spec, answers, previous_specs):
        """Spec'in gösterilip gösterilmeyeceğini dependency'lere göre kontrol et"""
        if 'depends_on' not in spec:
            return True
        
        for dependency in spec['depends_on']:
            dep_id = dependency['id']
            expected_value = dependency['eq']
            
            # Önceki spec'lerde bu ID'yi bul
            dep_spec_index = None
            for i, prev_spec in enumerate(previous_specs):
                if prev_spec['id'] == dep_id:
                    dep_spec_index = i
                    break
            
            if dep_spec_index is None or dep_spec_index >= len(answers):
                return False
            
            actual_answer = answers[dep_spec_index]
            
            # Boolean type için
            if previous_specs[dep_spec_index]['type'] == 'boolean':
                if (expected_value and actual_answer != 'Yes') or (not expected_value and actual_answer != 'No'):
                    return False
            # Single choice için
            elif previous_specs[dep_spec_index]['type'] == 'single_choice':
                # Option ID'sini bul
                selected_option_id = None
                for opt in previous_specs[dep_spec_index]['options']:
                    if opt['label']['en'] == actual_answer or opt['label']['tr'] == actual_answer:
                        selected_option_id = opt['id']
                        break
                if selected_option_id != expected_value:
                    return False
            # String değerler için
            elif actual_answer != expected_value:
                return False
        
        return True

    def _format_question(self, spec, language, reason=None):
        """Spec'i soru formatına çevir"""
        question_data = {
            'question': spec['label'][language],
            'emoji': spec.get('emoji', ''),
            'type': spec['type'],
            'id': spec['id'],
            'asked_spec_id': spec['id']  # ✅ Sorduğumuz spec'in ID'sini ekle
        }
        
        # Spec'e özgü tooltip ekle
        if 'tooltip' in spec and language in spec['tooltip']:
            question_data['tooltip'] = spec['tooltip'][language]
    
        # Soru sorma nedenine göre tooltip ekle (eğer spec'te yoksa)
        elif reason:
            tooltips = {
                'mandatory': {
                    'en': 'This is essential for good recommendations',
                    'tr': 'Bu iyi öneriler için gerekli'
                },
                'dependency': {
                    'en': 'Based on your previous answer',
                    'tr': 'Önceki cevabınıza göre'
                },
                'importance': {
                    'en': 'This significantly affects your options',
                    'tr': 'Bu seçeneklerinizi önemli ölçüde etkiler'
                },
                'quantification': {
                    'en': 'Need specific numbers for precise recommendations',
                    'tr': 'Kesin öneriler için sayısal değer gerekli'
                }
            }
            question_data['tooltip'] = tooltips.get(reason, {}).get(language, '')
        
        if spec['type'] == 'boolean':
            question_data['options'] = ['Yes', 'No', 'No preference'] if language == 'en' else ['Evet', 'Hayır', 'Farketmez']
        
        elif spec['type'] == 'single_choice':
            options = [opt['label'][language] for opt in spec['options']]
            # "Bilmiyorum" seçeneği ekle
            options.append('Not sure' if language == 'en' else 'Bilmiyorum')
            question_data['options'] = options
        
        elif spec['type'] == 'number':
            question_data['min'] = spec.get('min', 0)
            question_data['max'] = spec.get('max', 100)
            question_data['placeholder'] = f"Enter a number between {spec.get('min', 0)} and {spec.get('max', 100)}"
        
        return question_data

    def _generate_recommendations(self, category, preferences, specs, language):
        """AI-Enhanced Product Recommendations - Extract from detailed AI analysis"""
        try:
            print(f"🚀 AI-Enhanced Search Engine ile öneri oluşturuluyor: {category}")
            
            # Modern search sistemi için tercihleri hazırla
            search_preferences = self._prepare_search_preferences(category, preferences, language)
            
            # Modern Search Engine'i başlat
            from .search_engine import ModernSearchEngine
            search_engine = ModernSearchEngine()
            
            # Ürün arama yap
            search_results = search_engine.search_products(search_preferences)
            
            if search_results['status'] == 'success':
                # AI'dan gelen grounding results'u parse et ve gerçek ürün önerileri çıkar
                enhanced_recommendations = self._extract_real_products_from_ai_analysis(
                    search_results['grounding_results'],
                    preferences,
                    category,
                    language
                )
                
                return {
                    'type': 'ai_enhanced_recommendation',
                    'grounding_results': search_results['grounding_results'],
                    'shopping_results': enhanced_recommendations['shopping_results'],
                    'sources': search_results['sources'],
                    'recommendations': enhanced_recommendations['recommendations'],
                    'category': category,
                    'preferences': preferences,
                    'confidence_score': self._calculate_confidence_score(preferences, specs),
                    'ai_analysis': enhanced_recommendations['ai_analysis']
                }
            else:
                return {
                    'type': 'error',
                    'message': search_results.get('message', 'Arama sistemi hatası'),
                    'fallback_recommendations': self._get_fallback_recommendations(category, preferences, language)
                }
            
        except Exception as e:
            print(f"❌ AI-Enhanced search engine hatası: {e}")
            return {
                'type': 'error',
                'message': 'Arama sistemi geçici olarak kullanılamıyor',
                'fallback_recommendations': self._get_fallback_recommendations(category, preferences, language)
            }
    
    def _extract_budget_range(self, preferences):
        """Budget aralığını çıkar - 'k' formatını da destekler"""
        budget_band = preferences.get('budget_band', '')
        
        if not budget_band:
            return None, None
        
        print(f"🔍 Budget band parsing: '{budget_band}'")
        
        # "2-5k₺", "20-40k₺" formatını parse et
        import re
        
        # 'k' formatını kontrol et
        if 'k' in budget_band.lower():
            # "20-40k₺" -> [20000, 40000]  
            k_pattern = r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)k'
            k_match = re.search(k_pattern, budget_band.lower())
            
            if k_match:
                min_val = int(float(k_match.group(1)) * 1000)
                max_val = int(float(k_match.group(2)) * 1000)
                print(f"✅ K format parsed: {min_val} - {max_val}")
                return min_val, max_val
            
            # Tek k değeri "40k₺+" formatı
            single_k = re.search(r'(\d+(?:\.\d+)?)k', budget_band.lower())
            if single_k:
                base_value = int(float(single_k.group(1)) * 1000)
                if '+' in budget_band:
                    print(f"✅ K+ format parsed: {base_value} - {base_value * 2}")
                    return base_value, base_value * 2
                else:
                    print(f"✅ K max format parsed: None - {base_value}")
                    return None, base_value
        
        # Normal format "500-1000₺"
        normal_pattern = r'(\d+)\s*-\s*(\d+)'
        normal_match = re.search(normal_pattern, budget_band)
        
        if normal_match:
            min_val = int(normal_match.group(1))
            max_val = int(normal_match.group(2))
            print(f"✅ Normal format parsed: {min_val} - {max_val}")
            return min_val, max_val
        
        # Tek değer
        single_match = re.search(r'(\d+)', budget_band)
        if single_match:
            value = int(single_match.group(1))
            if '+' in budget_band:
                print(f"✅ Single+ format parsed: {value} - {value * 2}")
                return value, value * 2
            else:
                print(f"✅ Single format parsed: None - {value}")
                return None, value
        
        print(f"❌ Budget parsing failed for: '{budget_band}'")
        return None, None

    def _prepare_search_preferences(self, category, preferences, language):
        """Preferences'ları modern search sistemi için hazırla"""
        # Budget bilgisini çıkar
        budget_min, budget_max = self._extract_budget_range(preferences)
        
        # Özellikleri çıkar
        features = []
        for pref_id, value in preferences.items():
            if pref_id != 'budget_band' and value and value not in ['Bilmiyorum', 'Not sure', 'Farketmez', 'No preference']:
                if isinstance(value, bool):
                    if value:  # Sadece True olan özellikleri ekle
                        features.append(pref_id.replace('_', ' '))
                elif isinstance(value, str):
                    features.append(value)
        
        return {
            'category': category,
            'budget_min': budget_min,
            'budget_max': budget_max,
            'features': features,
            'language': language
        }
    
    def _extract_real_products_from_ai_analysis(self, grounding_results, preferences, category, language):
        """
        AI'ın detaylı analizinden gerçek ürün önerilerini çıkar
        """
        try:
            setup_gemini()
            model = get_gemini_model()
            
            # AI'ın grounding response'unu parse et
            ai_response = grounding_results.get('response', '')
            
            # Bütçe bilgisini al
            budget_min, budget_max = self._extract_budget_range(preferences)
            
            # Structured extraction prompt
            extraction_prompt = f"""
Sen bir e-ticaret uzmanısın. Aşağıdaki AI raporundan GERÇEK ürün bilgilerini çıkarıp yapılandırılmış JSON formatında döndür.

AI RAPORU:
{ai_response[:3000]}  

KULLANICI TERCİHLERİ:
- Kategori: {category}
- Bütçe: {budget_min}₺ - {budget_max}₺
- Özellikler: {json.dumps(preferences, ensure_ascii=False)}

GÖREV: 
1. Rapordaki GERÇEK ürün isimlerini, fiyatlarını ve özelliklerini çıkar
2. Her ürün için GERÇEK e-ticaret site linklerini oluştur (Trendyol, Hepsiburada, Teknosa vb.)
3. Kullanıcı tercihlerine en uygun 3-5 ürünü seç

ZORUNLU JSON FORMAT:
{{
  "ai_analysis": "AI raporunun özeti",
  "shopping_results": [
    {{
      "title": "GERÇEK ürün adı (örn: Samsung Galaxy S24 128GB)",
      "price": {{"value": 25000, "currency": "TRY", "display": "25.000 ₺"}},
      "source": "hepsiburada.com",
      "link": "https://www.hepsiburada.com/ara?q=samsung+galaxy+s24+128gb",
      "thumbnail": "https://via.placeholder.com/150x150?text=Product",
      "rating": 4.5,
      "reviews": 120,
      "delivery": "Ücretsiz kargo",
      "shipping": "1-2 gün"
    }}
  ],
  "recommendations": [
    {{
      "title": "GERÇEK ürün adı",
      "price": {{"value": 25000, "currency": "TRY", "display": "25.000 ₺"}},
      "features": ["GERÇEK özellik 1", "GERÇEK özellik 2"],
      "pros": ["GERÇEK avantaj 1", "GERÇEK avantaj 2"],
      "cons": ["GERÇEK dezavantaj 1"],
      "match_score": 95,
      "source_site": "hepsiburada.com",
      "product_url": "https://www.hepsiburada.com/ara?q=ürün+adı",
      "why_recommended": "Neden önerildi (GERÇEK özellikler)"
    }}
  ]
}}

ÖNEMLI: 
- Sadece raporda GEÇMİŞ GERÇEK ürünleri kullan (Apple MacBook Air M2, ASUS Zenbook, Dell XPS vb.)
- "Laptop Model 1" gibi MOCK ürünler kullanma
- Linkleri GERÇEK Türk e-ticaret sitelerine yönlendir
- Fiyatları rapordaki bilgilere göre ayarla

Sadece geçerli JSON döndür:
"""
            
            response = generate_with_retry(model, extraction_prompt, max_retries=2)
            
            if response and response.text:
                try:
                    # JSON parse et
                    json_content = response.text.strip()
                    if json_content.startswith('```json'):
                        json_content = json_content[7:-3]
                    elif json_content.startswith('```'):
                        json_content = json_content[3:-3]
                    
                    result = json.loads(json_content)
                    
                    # Linkleri doğrula ve onar
                    if 'shopping_results' in result:
                        for product in result['shopping_results']:
                            if 'link' in product:
                                print(f"🔗 Link doğrulaması: {product['title']}")
                                # Link validation'ı search engine'den kullan
                                from .search_engine import ModernSearchEngine
                                search_engine = ModernSearchEngine()
                                link_result = search_engine.validate_and_repair_link(
                                    product['link'], 
                                    product['title']
                                )
                                product['link'] = link_result['url']
                                product['link_status'] = link_result['status']
                                product['link_message'] = link_result['message']
                    
                    if 'recommendations' in result:
                        for product in result['recommendations']:
                            if 'product_url' in product:
                                print(f"🔗 Recommendation link doğrulaması: {product['title']}")
                                from .search_engine import ModernSearchEngine
                                search_engine = ModernSearchEngine()
                                link_result = search_engine.validate_and_repair_link(
                                    product['product_url'], 
                                    product['title']
                                )
                                product['product_url'] = link_result['url']
                                product['link_status'] = link_result['status']
                                product['link_message'] = link_result['message']
                    
                    print(f"✅ {len(result.get('recommendations', []))} gerçek ürün önerisi çıkarıldı")
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse failed: {e}")
                    print(f"Raw response: {response.text[:500]}")
                    return self._get_enhanced_fallback_recommendations(preferences, category, ai_response)
            
            return self._get_enhanced_fallback_recommendations(preferences, category, ai_response)
            
        except Exception as e:
            print(f"❌ Real product extraction error: {e}")
            return self._get_enhanced_fallback_recommendations(preferences, category, "")

    def _get_enhanced_fallback_recommendations(self, preferences, category, ai_analysis=""):
        """Enhanced fallback recommendations based on AI analysis"""
        
        # Bütçe bilgisini al
        budget_min, budget_max = self._extract_budget_range(preferences)
        
        # AI analizinden ürün isimlerini çıkarmaya çalış
        real_products = []
        if ai_analysis:
            # Rapordaki gerçek ürün isimlerini regex ile çıkar
            import re
            
            # MacBook, Galaxy, Dell XPS gibi gerçek ürün isimlerini ara
            product_patterns = [
                r'(MacBook [A-Za-z0-9\s]+)',
                r'(Galaxy [A-Za-z0-9\s]+)',
                r'(iPhone [A-Za-z0-9\s]+)',
                r'(Dell XPS [A-Za-z0-9\s]+)',
                r'(ASUS [A-Za-z0-9\s]+)',
                r'(HP [A-Za-z0-9\s]+)',
                r'(Lenovo [A-Za-z0-9\s]+)',
                r'(Xiaomi [A-Za-z0-9\s]+)',
                r'(Redmi [A-Za-z0-9\s]+)'
            ]
            
            for pattern in product_patterns:
                matches = re.findall(pattern, ai_analysis, re.IGNORECASE)
                for match in matches[:3]:  # İlk 3 match'i al
                    # Temizle ve formatla
                    product_name = re.sub(r'\s+', ' ', match.strip())
                    if len(product_name) > 5:  # Çok kısa isimleri filtrele
                        real_products.append(product_name)
        
        # Eğer gerçek ürün bulunamazsa kategori bazlı varsayılanlar
        if not real_products:
            if category == 'Laptop':
                real_products = [
                    'MacBook Air M2 13-inch',
                    'ASUS Zenbook 14 OLED',
                    'Dell XPS 13 Plus'
                ]
            elif category == 'Phone':
                real_products = [
                    'Samsung Galaxy S24 128GB',
                    'iPhone 15 128GB',
                    'Xiaomi Redmi Note 13 Pro'
                ]
            else:
                real_products = [f'{category} Pro Model']
        
        # Shopping results oluştur
        shopping_results = []
        recommendations = []
        
        for i, product_name in enumerate(real_products[:5]):
            # Fiyat hesapla (bütçe aralığında)
            if budget_min and budget_max:
                price_step = (budget_max - budget_min) / len(real_products)
                price = budget_min + (i * price_step)
            else:
                price = 15000 + (i * 5000)  # Varsayılan fiyat aralığı
            
            # Site seçimi (döngüsel)
            sites = ['hepsiburada.com', 'trendyol.com', 'teknosa.com', 'n11.com', 'vatanbilgisayar.com']
            selected_site = sites[i % len(sites)]
            
            # Arama URL'si oluştur
            search_query = product_name.lower().replace(' ', '+')
            if selected_site == 'hepsiburada.com':
                product_url = f"https://www.hepsiburada.com/ara?q={search_query}"
            elif selected_site == 'trendyol.com':
                product_url = f"https://www.trendyol.com/sr?q={search_query}"
            elif selected_site == 'teknosa.com':
                product_url = f"https://www.teknosa.com/arama?q={search_query}"
            elif selected_site == 'n11.com':
                product_url = f"https://www.n11.com/arama?q={search_query}"
            else:
                product_url = f"https://www.vatanbilgisayar.com/arama/?text={search_query}"
            
            shopping_results.append({
                "title": product_name,
                "price": {
                    "value": price,
                    "currency": "TRY",
                    "display": f"{price:,.0f} ₺".replace(',', '.')
                },
                "source": selected_site,
                "link": product_url,
                "thumbnail": f"https://via.placeholder.com/150x150?text={product_name.split()[0]}",
                "rating": 4.0 + (i * 0.2),
                "reviews": 50 + (i * 25),
                "delivery": "Ücretsiz kargo",
                "shipping": "1-2 gün",
                "link_status": "search_url",
                "link_message": f"{selected_site} arama sayfası"
            })
            
            # Recommendation oluştur
            recommendations.append({
                "title": product_name,
                "price": {
                    "value": price,
                    "currency": "TRY", 
                    "display": f"{price:,.0f} ₺".replace(',', '.')
                },
                "features": [f"Kaliteli {category.lower()}", "Güvenilir marka", "Yüksek performans"],
                "pros": ["İyi performans", "Güvenilir marka", "Olumlu kullanıcı yorumları"],
                "cons": ["Fiyat yüksek olabilir"],
                "match_score": 85 + (i * 2),
                "source_site": selected_site,
                "product_url": product_url,
                "link_status": "search_url",
                "link_message": f"{selected_site} arama sayfası",
                "why_recommended": f"AI analizine göre kullanıcı tercihlerinize uygun - {selected_site}'den arama"
            })
        
        return {
            "ai_analysis": ai_analysis[:500] + "..." if ai_analysis else "AI analizi mevcut değil",
            "shopping_results": shopping_results,
            "recommendations": recommendations
        }
        """Budget aralığını çıkar - 'k' formatını da destekler"""
        budget_band = preferences.get('budget_band', '')
        
        if not budget_band:
            return None, None
        
        print(f"🔍 Budget band parsing: '{budget_band}'")
        
        # "2-5k₺", "20-40k₺" formatını parse et
        import re
        
        # 'k' formatını kontrol et
        if 'k' in budget_band.lower():
            # "20-40k₺" -> [20000, 40000]  
            k_pattern = r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)k'
            k_match = re.search(k_pattern, budget_band.lower())
            
            if k_match:
                min_val = int(float(k_match.group(1)) * 1000)
                max_val = int(float(k_match.group(2)) * 1000)
                print(f"✅ K format parsed: {min_val} - {max_val}")
                return min_val, max_val
            
            # Tek k değeri "40k₺+" formatı
            single_k = re.search(r'(\d+(?:\.\d+)?)k', budget_band.lower())
            if single_k:
                base_value = int(float(single_k.group(1)) * 1000)
                if '+' in budget_band:
                    print(f"✅ K+ format parsed: {base_value} - {base_value * 2}")
                    return base_value, base_value * 2
                else:
                    print(f"✅ K max format parsed: None - {base_value}")
                    return None, base_value
        
        # Normal format "500-1000₺"
        normal_pattern = r'(\d+)\s*-\s*(\d+)'
        normal_match = re.search(normal_pattern, budget_band)
        
        if normal_match:
            min_val = int(normal_match.group(1))
            max_val = int(normal_match.group(2))
            print(f"✅ Normal format parsed: {min_val} - {max_val}")
            return min_val, max_val
        
        # Tek değer
        single_match = re.search(r'(\d+)', budget_band)
        if single_match:
            value = int(single_match.group(1))
            if '+' in budget_band:
                print(f"✅ Single+ format parsed: {value} - {value * 2}")
                return value, value * 2
            else:
                print(f"✅ Single format parsed: None - {value}")
                return None, value
        
        print(f"❌ Budget parsing failed for: '{budget_band}'")
        return None, None
    
    def _get_fallback_recommendations(self, category, preferences, language):
        """Fallback öneriler - doğru çalışan linklerle"""
        
        # Bütçe bilgisini al
        budget_min, budget_max = self._extract_budget_range(preferences)
        
        if category == 'Phone':
            return [
                {
                    'title': 'Samsung Galaxy A54 5G 128GB',
                    'price': {'value': min(budget_max or 15000, 15000), 'currency': 'TRY', 'display': f'{min(budget_max or 15000, 15000):.0f} ₺'},
                    'features': ['5G Destekli', '128GB Depolama', '50MP Kamera', '5000mAh Pil'],
                    'pros': ['Güvenilir marka', 'Uzun pil ömrü', 'İyi kamera'],
                    'cons': ['Orta segment işlemci'],
                    'match_score': 80,
                    'source_site': 'hepsiburada.com',
                    'product_url': 'https://www.hepsiburada.com/ara?q=samsung+galaxy+a54+5g',
                    'link_status': 'fallback',
                    'link_message': 'Hepsiburada arama sayfası',
                    'why_recommended': 'Güvenilir orta segment telefon'
                },
                {
                    'title': 'Xiaomi Redmi Note 12 256GB',
                    'price': {'value': min(budget_max or 10000, 10000), 'currency': 'TRY', 'display': f'{min(budget_max or 10000, 10000):.0f} ₺'},
                    'features': ['256GB Depolama', '48MP Kamera', '5000mAh Pil', 'Hızlı Şarj'],
                    'pros': ['Büyük depolama', 'Uygun fiyat', 'Hızlı şarj'],
                    'cons': ['MIUI arayüzü'],
                    'match_score': 75,
                    'source_site': 'trendyol.com',
                    'product_url': 'https://www.trendyol.com/sr?q=xiaomi+redmi+note+12+256gb',
                    'link_status': 'fallback',
                    'link_message': 'Trendyol arama sayfası',
                    'why_recommended': 'Fiyat/performans odaklı seçim'
                },
                {
                    'title': 'iPhone 13 128GB (Yenilenmiş)',
                    'price': {'value': min(budget_max or 20000, 20000), 'currency': 'TRY', 'display': f'{min(budget_max or 20000, 20000):.0f} ₺'},
                    'features': ['A15 Bionic Chip', '128GB Depolama', 'Dual Kamera', 'Face ID'],
                    'pros': ['iOS ekosistemi', 'Premium yapı', 'Uzun destek'],
                    'cons': ['Yenilenmiş ürün', 'Yüksek fiyat'],
                    'match_score': 85,
                    'source_site': 'teknosa.com',
                    'product_url': 'https://www.teknosa.com/arama?q=iphone+13+128gb',
                    'link_status': 'fallback',
                    'link_message': 'Teknosa arama sayfası',
                    'why_recommended': 'Apple kullanıcıları için uygun seçenek'
                }
            ]
        
        # Diğer kategoriler için genel fallback
        return [
            {
                'title': f'Önerilen {category}',
                'price': {'value': budget_min or 1000, 'currency': 'TRY', 'display': f'{budget_min or 1000:.0f} ₺'},
                'features': ['Kaliteli', 'Güvenilir'],
                'pros': ['İyi performans'],
                'cons': ['Sınırlı bilgi'],
                'match_score': 75,
                'source_site': 'hepsiburada.com',
                'product_url': f'https://www.hepsiburada.com/ara?q={category.lower()}',
                'link_status': 'fallback',
                'link_message': 'Hepsiburada arama sayfası',
                'why_recommended': 'Genel öneri - detaylı arama yapılamadı'
            }
        ]
    
    # Amazon entegrasyonu kaldırıldı - modern search sistemi kullanılacak

    def _build_gemini_prompt(self, category, preferences, language):
        """Gemini için gelişmiş prompt oluştur"""
        
        # Tercihleri analiz et
        priority_prefs = {}
        optional_prefs = {}
        
        for pref_id, value in preferences.items():
            if value is not None and value != 'Bilmiyorum' and value != 'Not sure' and value != 'Farketmez' and value != 'No preference':
                # Spec weight'ini bul
                spec_weight = 1.0
                for spec in self.categories[category]['specs']:
                    if spec['id'] == pref_id:
                        spec_weight = spec.get('weight', 1.0)
                        break
                
                if spec_weight >= 0.8:
                    priority_prefs[pref_id] = value
                else:
                    optional_prefs[pref_id] = value
        
        if language == 'tr':
            prompt = f"""Sen bir {category} uzmanısın. Türkiye pazarı için ürün önerisi yap.

Kullanıcı tercihleri:
{json.dumps(priority_prefs, indent=2, ensure_ascii=False)}
{json.dumps(optional_prefs, indent=2, ensure_ascii=False)}

3-4 ürün öner. Her ürün için:
- Ürün adı ve modeli
- Fiyat aralığı (TL)
- Ana özellikler
- Neden önerdiğin

Basit format kullan:
1. [ÜrünAdı] - [Fiyat] - [Özellikler]
2. [ÜrünAdı] - [Fiyat] - [Özellikler]
...

Örnek:
1. DJI Mini 3 - 15.000₺ - 4K kamera, 38dk uçuş süresi, kompakt tasarım"""
        else:
            prompt = f"""You are a {category} expert. Recommend products for Turkey market.

User preferences:
{json.dumps(priority_prefs, indent=2)}
{json.dumps(optional_prefs, indent=2)}

Recommend 3-4 products. For each:
- Product name and model
- Price range (TL)
- Key features
- Why you recommend it

Simple format:
1. [ProductName] - [Price] - [Features]
2. [ProductName] - [Price] - [Features]
...

Example:
1. DJI Mini 3 - 15,000₺ - 4K camera, 38min flight time, compact design"""
        
        return prompt

    def _parse_gemini_response(self, text):
        """Gemini response'unu parse et"""
        import re
        lines = text.strip().split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if not line or 'format' in line.lower() or 'örnek' in line.lower():
                continue
                
            # Format: ProductName - Price - Description
            parts = line.split(' - ')
            if len(parts) >= 3:
                name = parts[0].strip()
                price = parts[1].strip()
                description = parts[2].strip()
                
                recommendations.append({
                    'name': name,
                    'price': price,
                    'description': description
                })
        
        # Eğer parse edilemezse, ham metni döndür
        if not recommendations:
            recommendations.append({
                'name': 'Öneri',
                'price': '',
                'description': text
            })
        
        return recommendations
