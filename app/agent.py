import json
import os
from .config import setup_gemini, get_gemini_model

def detect_category_from_query(query):
    """Query'den kategori tespit et"""
    try:
        setup_gemini()
        model = get_gemini_model()
        
        prompt = (
            f"Kullanıcı şu ürünü arıyor: '{query}'. "
            "Bu isteğe en uygun kategori hangisi? Sadece kategori adını (ör: Headphones) tek kelime olarak döndür."
        )
        response = model.generate_content(prompt)
        category = response.text.strip().split()[0]
        
        # Validate against known categories
        with open('categories.json', 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        for cat in categories:
            if cat.lower() in category.lower():
                return cat
        return None
    except Exception:
        return None

class Agent:
    def __init__(self):
        self.categories = self.load_categories()

    def load_categories(self):
        try:
            with open('categories.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ categories.json dosyası bulunamadı!")
            return {}

    def handle(self, data):
        step = data.get('step', 0)
        category = data.get('category', '')
        answers = data.get('answers', [])
        language = data.get('language', 'en')
        
        print(f"🔄 Agent.handle çağrıldı - Step: {step}, Category: {category}, Answers: {answers}")
        print(f"📊 Raw data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if step == 0:
            # İlk adım: Kategori seçimi
            return {
                'question': 'What tech are you shopping for?' if language == 'en' else 'Hangi teknoloji ürününü arıyorsunuz?',
                'categories': list(self.categories.keys())
            }
        
        elif category and category in self.categories:
            specs = self.categories[category]['specs']
            
            # Kullanıcının mevcut tercihlerini analiz et
            preferences = self._analyze_current_preferences(answers, specs)
            
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
                return next_question
            else:
                # Tüm gerekli bilgiler toplandı, öneri ver
                return self._generate_recommendations(category, preferences, specs, language)
        
        else:
            return {'error': 'Invalid category or step'}

    def _analyze_current_preferences(self, answers, specs):
        """Mevcut cevapları tercih objesi haline getir"""
        preferences = {}
        
        print(f"🔍 _analyze_current_preferences:")
        print(f"  📊 answers_count={len(answers)}")
        print(f"  📋 specs_count={len(specs)}")
        print(f"  📝 answers={answers}")
        # Fix the budge t_band issue by ensuring proper formatting of spec IDs
        print(f"  🏷️ spec_ids=[{', '.join([spec['id'].strip() for spec in specs])}]")
        
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
                
                # Bu bir spec cevabı olarak işlendiyse, bu spec'i null olarak işaretle
                if i < len(specs):
                    spec_id = specs[i]['id']
                    if spec_id in preferences and spec_id != 'budget_band':
                        preferences[spec_id] = None
                        print(f"  ⚠️ Clearing {spec_id} since this was actually a budget answer")
    
        # Spec türleri ile cevap formatları arasında tutarlılık kontrolleri
        for i, answer in enumerate(answers):
            if i < len(specs) and answer is not None:
                spec = specs[i]
                spec_id = spec['id']
                
                # Tip uyumsuzluğu durumunda ek loglama
                print(f"  📋 Processing spec {i}: {spec_id} = '{answer}' (type: {spec['type']})")
                
                # Boolean tipinde beklenen ama farklı formatta gelen cevaplar için düzeltme
                if spec['type'] == 'boolean' and not any(kw in answer.lower() for kw in ['yes', 'no', 'evet', 'hayır', 'preference']):
                    print(f"    ⚠️ WARNING: Expected boolean but got '{answer}'. This might indicate a spec order mismatch.")
                
                # Single_choice için seçenek listesiyle eşleşmeyen cevaplar için uyarı
                if spec['type'] == 'single_choice':
                    options = [opt['label']['en'] for opt in spec['options']] + [opt['label']['tr'] for opt in spec['options']]
                    if answer not in options and 'preference' not in answer.lower() and 'sure' not in answer.lower():
                        print(f"    ⚠️ WARNING: Answer '{answer}' not in options list. This might indicate a spec order mismatch.")
            
            # Normal işleme devam et...
        
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
        
        # 4) Skor düşükse (bilgi yetersiz), yüksek weight'li eksikler
        # ANCAK budget sorulduysa bu adımı atla (yeteri kadar bilgi var demektir)
        if confidence_score < 0.7 and 'budget_band' not in preferences:
            high_weight_question = self._check_high_weight_missing(specs, preferences, language)
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
            'id': spec['id']
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
        """Gemini kullanarak öneri oluştur"""
        try:
            # Gemini için prompt oluştur
            prompt = self._build_gemini_prompt(category, preferences, language)
            
            # Gemini'den öneri al
            setup_gemini()
            model = get_gemini_model()
            response = model.generate_content(prompt)
            
            # Response'u parse et
            recommendations = self._parse_gemini_response(response.text)
            
            return {
                'type': 'recommendation',
                'recommendations': recommendations,
                'category': category,
                'preferences': preferences,
                'confidence_score': self._calculate_confidence_score(preferences, specs)
            }
            
        except Exception as e:
            print(f"❌ Gemini hatası: {e}")
            return {
                'type': 'error',
                'message': 'Sorry, I could not generate recommendations at this time.' if language == 'en' 
                          else 'Üzgünüm, şu anda öneri oluşturamıyorum.'
            }

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
            prompt = f"""
            Türkiye pazarında {category} kategorisinde ürün önerisi yap.
            
            ÖNCELIKLI TERCİHLER (MUTLAKA KARŞILANMALI):
            {json.dumps(priority_prefs, indent=2, ensure_ascii=False)}
            
            İSTEĞE BAĞLI TERCİHLER:
            {json.dumps(optional_prefs, indent=2, ensure_ascii=False)}
            
            Lütfen:
            1. Öncelikli tercihleri MUTLAKA karşılayan 3-4 ürün öner
            2. Her ürün için model adı, öne çıkan özellikler, fiyat aralığı
            3. Neden önerdiğini kısaca açıkla
            4. Akakce.com arama linki ekle
            5. En uygun seçimi belirt
            
            Format (her ürün için):
            [⭐ EN ÇOK ÖNERİLEN] ÜrünAdı - FiyatAralığı - ÖneÇıkanÖzellikler - https://www.akakce.com/arama/?q=ÜrünAdı
            
            Önerme kriterleri:
            - Türkiye'de kolayca bulunabilir olmalı
            - Gerçekçi fiyat aralıkları ver
            - Kullanıcının öncelikli tercihlerini %100 karşılamalı
            """
        else:
            prompt = f"""
            Recommend {category} products for the Turkish market.
            
            PRIORITY PREFERENCES (MUST BE MET):
            {json.dumps(priority_prefs, indent=2)}
            
            OPTIONAL PREFERENCES:
            {json.dumps(optional_prefs, indent=2)}
            
            Please:
            1. Recommend 3-4 products that DEFINITELY meet priority preferences
            2. Include model name, key features, price range for each
            3. Briefly explain why you recommend each
            4. Add Akakce.com search links
            5. Mark the best choice
            
            Format (for each product):
            [⭐ TOP PICK] ProductName - PriceRange - KeyFeatures - https://www.akakce.com/arama/?q=ProductName
            
            Criteria:
            - Must be easily available in Turkey
            - Give realistic price ranges
            - Must 100% satisfy priority preferences
            """
        
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
                
            # Format: ProductName - Price - Description - Link
            parts = line.split(' - ')
            if len(parts) >= 3:
                name = parts[0].strip()
                price = parts[1].strip()
                description = parts[2].strip()
                
                # Link varsa al, yoksa oluştur
                if len(parts) >= 4 and 'http' in parts[3]:
                    link = parts[3].strip()
                else:
                    # Akakce search linki oluştur
                    search_query = re.sub(r'[^\w\s]', '', name)
                    search_query = re.sub(r'\s+', '+', search_query)
                    link = f'https://www.akakce.com/arama/?q={search_query}'
                
                recommendations.append({
                    'name': name,
                    'price': price,
                    'description': description,
                    'link': link
                })
        
        # Eğer parse edilemezse, ham metni döndür
        if not recommendations:
            recommendations.append({
                'name': 'Öneri',
                'price': '',
                'description': text,
                'link': ''
            })
        
        return recommendations
