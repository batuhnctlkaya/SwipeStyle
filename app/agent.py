def detect_category_from_query(query):
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
    def __init__(self):
        with open('categories.json', 'r', encoding='utf-8') as f:
            self.categories = json.load(f)
        self.state = {}

    def handle(self, data):
        step = data.get('step', 0)
        category = data.get('category')
        answers = data.get('answers', [])

        # Step 0: ask for category if not provided
        if step == 0 or not category:
            return {'question': 'What tech are you shopping for?', 'options': list(self.categories.keys())}

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
        answer_str = ', '.join(answers)
        return (
            f"Türk pazarında '{category}' kategorisinde, şu özelliklere sahip ürünler öner: {answer_str}. "
            "Her ürün için isim, tahmini fiyat ve doğrudan akakce.com'daki ürün sayfasına giden bir link ver. Sadece aşağıdaki örnekteki gibi kısa bir tablo olarak dön.\n"
            "\nÖrnek çıktı:\n"
            "ASUS Vivobook 15 X1502ZA (i5-1235U, 16GB RAM, 512GB SSD) - 15.000 TL - https://www.akakce.com/arama/?q=ASUS+Vivobook+15+X1502ZA\n"
            "HP Victus 15-fa0010nt (i5, 16GB RAM, 512GB SSD) - 18.000 TL - https://www.akakce.com/arama/?q=HP+Victus+15-fa0010nt\n"
            "\nLütfen sadece bu formatta dön: Ürün Adı - Fiyat - Link."
        )

    def _parse_gemini_links_response(self, text):
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
