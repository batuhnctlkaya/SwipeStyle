# SwipeStyle Logging System

Bu sistem, SwipeStyle agent'ının ürettiği tüm çıktıları ve API yanıtlarını ayrı dosyalarda loglar.

## Log Dosyaları

### 1. `debug_log.txt`
- **Amaç**: API endpoint'lerine gelen input verilerini loglar
- **İçerik**: `/ask` ve `/detect_category` endpoint'lerine gelen veriler
- **Format**: Basit metin formatı

### 2. `agent_output_log.txt` (YENİ)
- **Amaç**: Agent'ın ürettiği tüm çıktıları detaylı şekilde loglar
- **İçerik**: 
  - Agent'ın sorduğu sorular
  - Üretilen öneriler
  - Kategori tespit sonuçları
  - API yanıtları
  - Hata mesajları
- **Format**: Timestamp'li, kategorize edilmiş, JSON formatında

## Log Türleri

### Agent Output Log'da bulunan türler:
- `category_selection`: İlk kategori seçim ekranı
- `follow_up_question`: Devam eden sorular
- `recommendations`: Ürün önerileri
- `error`: Hata durumları
- `category_detection`: Kategori tespit sonuçları
- `api_response_/ask`: /ask endpoint yanıtları
- `api_response_/detect_category`: /detect_category endpoint yanıtları

## Kullanım Araçları

### 1. Log Görüntüleyici (`view_logs.py`)
```bash
# Tüm logları göster
python view_logs.py

# Son 10 girişi göster
python view_logs.py --last 10

# Sadece önerileri göster
python view_logs.py --type recommendation

# Canlı takip modu
python view_logs.py --tail
```

### 2. Log Temizleyici (`clear_logs.py`)
```bash
# Sadece agent output log'unu temizle
python clear_logs.py

# Tüm logları temizle
python clear_logs.py --all

# Backup alarak temizle
python clear_logs.py --backup --all
```

## Hangi Sorunları Tespit Edebilirsiniz?

### 1. Agent'ın Yanlış Sorular Sorması
- `follow_up_question` türündeki logları inceleyin
- Soru akışının mantığını kontrol edin
- Dependency'lerin doğru çalışıp çalışmadığını görün

### 2. Önerilerin Kalitesiz Olması
- `recommendations` türündeki logları inceleyin
- Input preferences'ları kontrol edin
- Modern Search Engine sonuçlarını görün

### 3. Kategori Tespitinde Sorunlar
- `category_detection` türündeki logları inceleyin
- Hangi yöntemle kategori tespit edildiğini görün
- Başarısız tespit durumlarını analiz edin

### 4. API Yanıtlarında Tutarsızlık
- `api_response_*` türündeki logları inceleyin
- Input-output eşleşmelerini kontrol edin

## Örnek Log Girişi

```
⏰ [2024-01-15 14:30:25] Agent Output Type: follow_up_question
================================================================================
📥 INPUT DATA:
{
  "step": 2,
  "category": "Phone",
  "answers": ["Yes"],
  "language": "tr"
}
----------------------------------------
📤 OUTPUT DATA:
{
  "question": "Pil ömrü ne kadar önemli?",
  "type": "single_choice",
  "options": ["Çok önemli", "Orta", "Önemli değil"],
  "emoji": "🔋",
  "progress": 40
}
```

## Debug Önerileri

1. **İlk test**: `python view_logs.py --last 5` ile son 5 girişi kontrol edin
2. **Sorun analizi**: Problematik yanıtların input verilerini inceleyin
3. **Akış takibi**: Bir kategoride baştan sona kadar olan akışı takip edin
4. **Canlı debug**: `python view_logs.py --tail` ile gerçek zamanlı takip yapın

Bu logging sistemi sayesinde agent'ın hangi aşamada ne tür kararlar aldığını detaylı şekilde görebilir ve sorunları daha kolay tespit edebilirsiniz.
