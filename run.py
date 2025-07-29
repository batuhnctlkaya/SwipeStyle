# Ensure requirements are installed at startup
import subprocess
import sys
import os
def install_requirements():
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
install_requirements()

import json
from flask import Flask, request, jsonify, send_from_directory
from app.agent import Agent
from app.category_agent import CategoryAgent

app = Flask(__name__, static_folder='website')
category_agent = CategoryAgent()
agent = Agent()

@app.route('/detect_category', methods=['POST'])
def detect_category():
    data = request.json
    query = data.get('query', '')
    # Use CategoryAgent to get or create the category
    category, created = category_agent.get_or_create_category(query)
    if not category:
        return jsonify({'error': 'Kategori oluşturulamadı veya tespit edilemedi. Lütfen daha açık bir istek girin veya daha sonra tekrar deneyin.'}), 400
    return jsonify({'category': category, 'created': created})

@app.route('/')
def index():
    return app.send_static_file('main.html')

# Serve static files (main.js, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/categories')
def get_categories():
    # Use CategoryAgent to get categories and their specs
    cats = category_agent.categories
    return jsonify(cats)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    response = agent.handle(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=8080)