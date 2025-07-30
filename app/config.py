import os
from dotenv import load_dotenv
import google.generativeai as genai

def setup_gemini():
    """Gemini API'yi yapılandır"""
    load_dotenv()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    return False

def get_gemini_model():
    """Gemini modelini döndür"""
    return genai.GenerativeModel('gemini-2.5-flash')
