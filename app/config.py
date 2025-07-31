import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

def setup_gemini():
    """Gemini API'yi yapılandır"""
    load_dotenv()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    return False

def get_gemini_model():
    """Gemini modelini döndür - optimized for better performance"""
    return genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.9,
            top_k=32,
            max_output_tokens=2048,
        )
    )

def generate_with_retry(model, prompt, max_retries=3, delay=2):
    """Gemini API'ye retry mekanizması ile istek gönder"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Gemini API isteği (deneme {attempt + 1}/{max_retries})")
            response = model.generate_content(prompt)
            if response and response.text:
                print(f"✅ Gemini API başarılı (deneme {attempt + 1})")
                return response
            else:
                print(f"⚠️ Boş yanıt alındı (deneme {attempt + 1})")
        except Exception as e:
            print(f"❌ Gemini API hatası (deneme {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"⏳ {delay} saniye bekleniyor...")
                time.sleep(delay)
                delay *= 1.5  # Exponential backoff
            else:
                raise e
    return None
