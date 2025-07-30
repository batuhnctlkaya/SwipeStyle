
import json
from flask import Flask, request, jsonify, send_from_directory
from app.agent import Agent
from app.agent import detect_category_from_query

app = Flask(__name__, static_folder='website')
agent = Agent()
@app.route('/detect_category', methods=['POST'])
# Bu fonksiyon http://localhost:8080/detect_category adresine POST isteği geldiğinde çalışır
def detect_category():
    data = request.json
    print("=" * 50)
    print("🔍 /detect_category endpointine gelen veri:", data)
    print("=" * 50)
    # Dosyaya da yazdıralım
    with open('debug_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"🔍 /detect_category veri: {data}\n")
    query = data.get('query', '')
    category = detect_category_from_query(query)
    return jsonify({'category': category})

@app.route('/') # Bu fonksiyon http://localhost:8080/ (ana sayfa) adresine GET isteği geldiğinde çalışır
def index():
    return app.send_static_file('main.html')

@app.route('/<path:filename>')
# Bu fonksiyon herhangi bir dosya ismi için çalışır
# Örnek: http://localhost:8080/main.js
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/categories')
# Bu fonksiyon http://localhost:8080/categories adresine GET isteği geldiğinde çalışır
def get_categories():
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    return jsonify(categories)

@app.route('/ask', methods=['POST'])
# Bu fonksiyon http://localhost:8080/ask adresine POST isteği geldiğinde çalışır
def ask():
    data = request.json
    print("=" * 50)
    print("📩 /ask endpointine gelen veri:", data)
    print("=" * 50)
    # Dosyaya da yazdıralım
    with open('debug_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"📩 /ask veri: {data}\n")
    response = agent.handle(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=8080)