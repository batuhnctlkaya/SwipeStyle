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

        if step == 0:
            return {'question': 'Hangi ürün türünü seçmek istersiniz?', 'options': list(self.categories.keys())}
        elif step == 1 and category:
            specs = self.categories.get(category, {}).get('specs', [])
            if specs:
                return {'question': f'{category} için hangi özellikleri tercih edersiniz?', 'options': specs}
            else:
                return {'question': 'Bu kategori için özellik bulunamadı.', 'options': []}
        elif step == 2 and category and answers:
            # Use Gemini for recommendations
            prompt = self._build_prompt(category, answers)
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                recs = self._parse_gemini_response(response.text)
                return {'recommendations': recs}
            except Exception as e:
                return {'error': f'Gemini API hatası: {str(e)}'}
        else:
            return {'error': 'Geçersiz adım veya veri.'}

    def _build_prompt(self, category, answers):
        answer_str = ', '.join(answers)
        return (
            f"Türk pazarında '{category}' kategorisinde, şu özelliklere sahip ürünler öner: {answer_str}. "
            "Farklı fiyat aralıklarında 2-3 ürün öner, isim ve tahmini fiyatı belirt. Sadece tablo veya kısa liste olarak dön."
        )

    def _parse_gemini_response(self, text):
        # Simple parser for Gemini's response
        lines = text.split('\n')
        recs = []
        for line in lines:
            parts = line.split('-')
            if len(parts) >= 2:
                name = parts[0].strip()
                price = parts[1].strip()
                recs.append({'name': name, 'price': price})
        if not recs:
            recs.append({'name': text.strip(), 'price': ''})
        return recs
