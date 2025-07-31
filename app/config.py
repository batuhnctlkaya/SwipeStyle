"""
SwipeStyle Yapılandırma Modülü
==============================

Bu modül, SwipeStyle uygulamasının Gemini AI yapılandırması ve yardımcı fonksiyonlarını içerir.
Gemini API'yi yapılandırır, model nesnelerini oluşturur ve retry mekanizmaları sağlar.

Ana Fonksiyonlar:
- setup_gemini(): Gemini API'yi yapılandırır
- get_gemini_model(): Optimize edilmiş Gemini modeli döner
- generate_with_retry(): Retry mekanizması ile API istekleri gönderir

Özellikler:
- Otomatik API yapılandırması
- Optimize edilmiş model parametreleri
- Exponential backoff retry mekanizması
- Hata yönetimi ve loglama

Gereksinimler:
- Google Generative AI (Gemini)
- .env dosyasında GEMINI_API_KEY
- python-dotenv paketi
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

def setup_gemini():
    """
    Gemini API'yi yapılandırır ve başlatır.
    
    .env dosyasından API anahtarını okur ve Gemini API'yi yapılandırır.
    Başarılı yapılandırma durumunda True, başarısız durumda False döner.
    
    Returns:
        bool: Yapılandırma başarılı mı?
        
    Örnek:
        >>> if setup_gemini():
        ...     print("Gemini API başarıyla yapılandırıldı")
        ... else:
        ...     print("Gemini API yapılandırılamadı")
    """
    load_dotenv()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    return False

def get_gemini_model():
    """
    Optimize edilmiş Gemini modeli döner.
    
    SwipeStyle uygulaması için özel olarak yapılandırılmış
    Gemini modeli oluşturur. Sıcaklık, top_p, top_k ve
    max_output_tokens parametreleri optimize edilmiştir.
    
    Returns:
        genai.GenerativeModel: Yapılandırılmış Gemini modeli
        
    Örnek:
        >>> model = get_gemini_model()
        >>> response = model.generate_content("Merhaba")
    """
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
    """
    Gemini API'ye retry mekanizması ile istek gönderir.
    
    Bu fonksiyon, API isteklerini güvenilir hale getirmek için
    exponential backoff retry mekanizması kullanır. Her başarısız
    denemeden sonra bekleme süresi artırılır.
    
    Args:
        model (genai.GenerativeModel): Gemini model nesnesi
        prompt (str): AI'ya gönderilecek prompt metni
        max_retries (int): Maksimum deneme sayısı (varsayılan: 3)
        delay (int): İlk deneme arası bekleme süresi (varsayılan: 2)
        
    Returns:
        genai.types.GenerateContentResponse or None: API yanıtı veya None
        
    Raises:
        Exception: Tüm denemeler başarısız olduğunda
        
    Örnek:
        >>> model = get_gemini_model()
        >>> response = generate_with_retry(model, "Kategori önerisi yap")
        >>> if response:
        ...     print(response.text)
    """
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
