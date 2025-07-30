"""
Çeviri Servisi
=============

Bu modül, Türkçe ve İngilizce arasında çeviri yapar.
Google Translate API'sı ve Gemini AI kullanarak kaliteli çeviriler sağlar.

Ana Özellikler:
- Türkçe <-> İngilizce çeviri
- Gemini AI ile bağlamsal çeviri
- Fallback olarak Google Translate
- Kategori soruları için optimize edilmiş

Kullanım:
    translator = TranslationService()
    english_text = translator.translate("Kablosuz kulaklık ister misiniz?", "tr", "en")
"""

import os
import google.generativeai as genai
from googletrans import Translator
import logging
from typing import Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationService:
    """
    Çeviri servisi sınıfı.
    
    Gemini AI ve Google Translate kullanarak kaliteli çeviriler yapar.
    Özellikle e-ticaret ve ürün kategorileri için optimize edilmiştir.
    """
    
    def __init__(self):
        """
        Çeviri servisini başlatır.
        
        Gemini API ve Google Translate'i configure eder.
        """
        # Gemini AI setup
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            logger.warning("GEMINI_API_KEY bulunamadı. Sadece Google Translate kullanılacak.")
            self.gemini_model = None
        
        # Google Translate setup
        try:
            self.google_translator = Translator()
        except Exception as e:
            logger.error(f"Google Translate başlatılamadı: {str(e)}")
            self.google_translator = None
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Metni kaynak dilden hedef dile çevirir.
        
        Args:
            text (str): Çevrilecek metin
            source_lang (str): Kaynak dil kodu ("tr", "en")
            target_lang (str): Hedef dil kodu ("tr", "en")
            
        Returns:
            str: Çevrilmiş metin
            
        Örnek:
            translator.translate("Do you want wireless headphones?", "en", "tr")
            # -> "Kablosuz kulaklık ister misiniz?"
        """
        if source_lang == target_lang:
            return text
        
        if not text or not text.strip():
            return text
        
        # Önce Gemini AI ile dene
        if self.gemini_model:
            gemini_result = self._translate_with_gemini(text, source_lang, target_lang)
            if gemini_result:
                return gemini_result
        
        # Fallback: Google Translate
        return self._translate_with_google(text, source_lang, target_lang)
    
    def _translate_with_gemini(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Gemini AI ile çeviri yapar.
        
        Args:
            text (str): Çevrilecek metin
            source_lang (str): Kaynak dil
            target_lang (str): Hedef dil
            
        Returns:
            Optional[str]: Çevrilmiş metin veya None
        """
        try:
            lang_names = {
                "tr": "Turkish",
                "en": "English"
            }
            
            source_name = lang_names.get(source_lang, source_lang)
            target_name = lang_names.get(target_lang, target_lang)
            
            prompt = f"""
            Translate the following {source_name} text to {target_name}.
            Keep the context of e-commerce and product categories.
            Only return the translated text, nothing else.
            
            Text to translate: {text}
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                translated = response.text.strip()
                # Remove quotes if present
                if translated.startswith('"') and translated.endswith('"'):
                    translated = translated[1:-1]
                if translated.startswith("'") and translated.endswith("'"):
                    translated = translated[1:-1]
                
                logger.info(f"Gemini çevirisi: {text} -> {translated}")
                return translated
                
        except Exception as e:
            logger.error(f"Gemini çeviri hatası: {str(e)}")
        
        return None
    
    def _translate_with_google(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Google Translate ile çeviri yapar.
        
        Args:
            text (str): Çevrilecek metin
            source_lang (str): Kaynak dil
            target_lang (str): Hedef dil
            
        Returns:
            str: Çevrilmiş metin
        """
        try:
            if self.google_translator:
                result = self.google_translator.translate(text, src=source_lang, dest=target_lang)
                if result and result.text:
                    logger.info(f"Google Translate çevirisi: {text} -> {result.text}")
                    return result.text
        except Exception as e:
            logger.error(f"Google Translate hatası: {str(e)}")
        
        # Son çare: text'i olduğu gibi döndür
        logger.warning(f"Çeviri yapılamadı, orijinal metin döndürülüyor: {text}")
        return text
    
    def translate_questions_batch(self, questions: List[Dict], source_lang: str, target_lang: str) -> List[Dict]:
        """
        Bir soru listesini toplu olarak çevirir.
        
        Args:
            questions (List[Dict]): Soru listesi [{"key": "...", "question": "...", "emoji": "..."}]
            source_lang (str): Kaynak dil
            target_lang (str): Hedef dil
            
        Returns:
            List[Dict]: Çevrilmiş soru listesi
        """
        translated_questions = []
        
        for question in questions:
            translated_question = question.copy()
            
            if "question" in question:
                translated_question["question"] = self.translate(
                    question["question"], 
                    source_lang, 
                    target_lang
                )
            
            translated_questions.append(translated_question)
        
        return translated_questions
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Desteklenen dil listesini döndürür.
        
        Returns:
            Dict[str, str]: Dil kod - isim eşleştirmesi
        """
        return {
            "tr": "Türkçe",
            "en": "English"
        }
    
    def auto_translate_category_specs(self, category_name: str, turkish_specs: List[Dict]) -> List[Dict]:
        """
        Bir kategorinin Türkçe sorularını otomatik olarak İngilizceye çevirir.
        
        Args:
            category_name (str): Kategori adı
            turkish_specs (List[Dict]): Türkçe sorular
            
        Returns:
            List[Dict]: Hem Türkçe hem İngilizce içeren sorular
        """
        enhanced_specs = []
        
        for spec in turkish_specs:
            enhanced_spec = spec.copy()
            
            # Türkçe soruyu İngilizceye çevir
            if "question" in spec:
                english_question = self.translate(spec["question"], "tr", "en")
                enhanced_spec["question_tr"] = spec["question"]
                enhanced_spec["question_en"] = english_question
                # Backward compatibility için question alanını tut
                enhanced_spec["question"] = spec["question"]
            
            enhanced_specs.append(enhanced_spec)
        
        logger.info(f"Kategori {category_name} için {len(enhanced_specs)} soru çevrildi")
        return enhanced_specs


# Test fonksiyonu
if __name__ == "__main__":
    translator = TranslationService()
    
    # Test çevirileri
    test_texts = [
        ("Kablosuz kulaklık ister misiniz?", "tr", "en"),
        ("Do you want wireless headphones?", "en", "tr"),
        ("Bu ürünün fiyat aralığı nedir?", "tr", "en"),
        ("What is your budget range?", "en", "tr")
    ]
    
    print("=== Çeviri Testleri ===")
    for text, source, target in test_texts:
        translated = translator.translate(text, source, target)
        print(f"{source} -> {target}: {text} -> {translated}")
    
    # Toplu çeviri testi
    print("\n=== Toplu Çeviri Testi ===")
    questions = [
        {"key": "wireless", "question": "Kablosuz özellik ister misiniz?", "emoji": "📶"},
        {"key": "price", "question": "Bütçeniz nedir?", "emoji": "💰"}
    ]
    
    translated_questions = translator.translate_questions_batch(questions, "tr", "en")
    for q in translated_questions:
        print(f"- {q['question']} ({q['emoji']})")
