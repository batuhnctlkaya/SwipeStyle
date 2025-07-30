"""
SwipeStyle Ana Agent Modülü
===========================

Bu modül, SwipeStyle uygulamasının ana akıllı agent'ını içerir.
Kullanıcı etkileşimlerini yönetir, soru-cevap akışını kontrol eder
ve Gemini AI kullanarak ürün önerileri sunar.

Ana Sınıflar:
- Agent: Ana agent sınıfı, kullanıcı etkileşimlerini yönetir

Fonksiyonlar:
- detect_category_from_query: Kullanıcı sorgusundan kategori tespiti

Gereksinimler:
- Google Generative AI (Gemini)
- categories.json dosyası
- .env dosyasında GEMINI_API_KEY
"""

def detect_category_from_query(query):
    """
    Kullanıcı sorgusundan kategori tespiti yapar.
    
    Bu fonksiyon, Gemini AI kullanarak kullanıcının yazdığı metinden
    en uygun ürün kategorisini tespit eder.
    
    Args:
        query (str): Kullanıcının arama sorgusu (örn: "kablosuz kulaklık")
        
    Returns:
        str or None: Tespit edilen kategori adı veya None
        
    Örnek:
        >>> detect_category_from_query("kablosuz kulaklık")
        "Headphones"
    """
    # Use Gemini to extract category from user query
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (
            f"Kullanıcı şu ürünü arıyor: '{query}'. "
            "Bu isteğe en uygun kategori hangisi? Sadece kategori adını (ör: Mouse, Headphones, Phone, Laptop) tek kelime olarak döndür."
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

import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class Agent:
    """
    SwipeStyle Ana Agent Sınıfı
    
    Bu sınıf, kullanıcı etkileşimlerini yönetir ve ürün önerileri sunar.
    Soru-cevap akışını kontrol eder, kategorileri yükler ve
    Gemini AI ile akıllı öneriler üretir.
    
    Özellikler:
    - categories: Yüklenen kategori listesi
    - state: Kullanıcı oturum durumu
    
    Ana Metodlar:
    - handle(): Ana etkileşim yöneticisi
    - _build_prompt_with_links(): Gemini için prompt oluşturur
    - _parse_gemini_links_response(): AI yanıtını ayrıştırır
    """
    
    def __init__(self):
        """
        Agent'ı başlatır ve kategorileri yükler.
        
        categories.json dosyasından kategori listesini okur
        ve kullanıcı durumu için boş state oluşturur.
        """
        with open('categories.json', 'r', encoding='utf-8') as f:
            self.categories = json.load(f)
        self.state = {}

    def handle(self, data):
        """
        Kullanıcı etkileşimini yönetir ve uygun yanıtı döndürür.
        
        Bu metod, kullanıcının hangi adımda olduğunu kontrol eder:
        - Step 0: Kategori seçimi
        - Step 1-N: Soru-cevap akışı
        - Step N+1: Ürün önerileri
        
        Args:
            data (dict): Kullanıcı verisi
                - step: Mevcut adım (int)
                - category: Seçilen kategori (str)
                - answers: Verilen cevaplar listesi (list)
                
        Returns:
            dict: Yanıt verisi
                - question: Soru metni
                - options: Seçenekler listesi
                - emoji: Soru emojisi
                - recommendations: Ürün önerileri
                - error: Hata mesajı
        """
        step = data.get('step', 0)
        category = data.get('category')
        answers = data.get('answers', [])

        # Step 0: ask for category if not provided
        if step == 0 or not category:
            return {
                'question': 'Hangi teknoloji ürününü arıyorsunuz? 🛍️', 
                'options': list(self.categories.keys())
            }

        # Validate category
        if category not in self.categories:
            return {'error': f"Kategori bulunamadı: {category}. Lütfen geçerli bir kategori seçin."}

        specs = self.categories[category].get('specs', [])
        if not specs:
            return {'error': f"'{category}' için özellik bulunamadı."}

        # Ask spec questions one by one
        if step > 0 and step <= len(specs):
            spec = specs[step-1]
            return {
                'question': spec.get('question', ''),
                'emoji': spec.get('emoji', ''),
                'options': ['Yes', 'No']
            }

        # After all questions, recommend products
        if step > len(specs):
            selected_specs = [specs[i]['key'] for i, ans in enumerate(answers) if ans == 'Yes']
            prompt = self._build_prompt_with_links(category, selected_specs)
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                recs = self._parse_gemini_links_response(response.text)
                return {'recommendations': recs}
            except Exception as e:
                return {'error': f'Gemini API hatası: {str(e)}'}

        # Fallback error
        return {'error': 'Geçersiz adım veya veri.'}

    def _build_prompt_with_links(self, category, answers):
        """
        Gemini AI için ürün önerisi prompt'u oluşturur.
        
        Bu metod, seçilen kategori ve kullanıcı cevaplarına göre
        Gemini AI'ya gönderilecek prompt'u hazırlar. Prompt,
        Türk pazarındaki ürünleri önermesi için tasarlanmıştır.
        
        Args:
            category (str): Ürün kategorisi (örn: "Headphones")
            answers (list): Kullanıcının "Yes" dediği özellikler listesi
            
        Returns:
            str: Gemini AI için hazırlanmış prompt metni
            
        Örnek:
            >>> _build_prompt_with_links("Headphones", ["Kablosuz", "ANC"])
            "Türk pazarında google shop üzerinde 'Headphones' kategorisinde..."
        """
        answer_str = ', '.join(answers)
        return (
            f"Türk pazarında google shop üzerinde '{category}' kategorisinde, şu özelliklere sahip ürünler öner: {answer_str}. "
            "Her ürün için isim, tahmini fiyat ve doğrudan akakce.com'daki ürün sayfasına giden bir link ver. Sadece aşağıdaki örnekteki gibi kısa bir tablo olarak dön.\n"
            "\nÖrnek çıktı:\n"
            "ASUS Vivobook 15 X1502ZA (i5-1235U, 16GB RAM, 512GB SSD) - 15.000 TL - (LINK)\n"
            "HP Victus 15-fa0010nt (i5, 16GB RAM, 512GB SSD) - 18.000 TL - (LINK)\n"
            "\nLütfen sadece bu formatta dön: Ürün Adı - Fiyat - Link."
        )

    def _parse_gemini_links_response(self, text):
        """
        Gemini AI yanıtını ayrıştırır ve ürün önerilerini formatlar.
        
        Bu metod, Gemini AI'dan gelen metin yanıtını alır ve
        ürün adı, fiyat ve link bilgilerini ayrıştırır. Ayrıca
        her ürün için akakce.com arama linki oluşturur.
        
        Args:
            text (str): Gemini AI'dan gelen ham yanıt metni
            
        Returns:
            list: Ürün önerileri listesi
                Her öneri: {
                    'name': 'Ürün adı',
                    'price': 'Fiyat bilgisi', 
                    'link': 'Akakce arama linki'
                }
                
        Örnek:
            >>> _parse_gemini_links_response("Sony WH-1000XM4 - 2.500 TL")
            [{'name': 'Sony WH-1000XM4', 'price': '2.500 TL', 'link': 'https://www.akakce.com/arama/?q=Sony+WH1000XM4'}]
        """
        # Parse Gemini response for name and price, then generate Akakce search link
        import re
        lines = text.split('\n')
        recs = []
        for line in lines:
            # Ignore lines that are just 'Fiyat', 'Link', or empty
            if not line.strip() or 'Fiyat' in line or 'Link' in line:
                continue
            parts = [p.strip() for p in re.split(r'\||-', line) if p.strip()]
            if len(parts) >= 2:
                name = parts[0]
                price = parts[1]
                # Generate Akakce search URL
                search_query = re.sub(r'[^\w\s]', '', name)
                search_query = re.sub(r'\s+', '+', search_query)
                akakce_url = f'https://www.akakce.com/arama/?q={search_query}'
                recs.append({'name': name, 'price': price, 'link': akakce_url})
        if not recs:
            recs.append({'name': text.strip(), 'price': '', 'link': ''})
        return recs
