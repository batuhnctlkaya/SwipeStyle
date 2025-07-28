import json
from flask import Flask, request, jsonify, send_from_directory
from app.agent import Agent

app = Flask(__name__, static_folder='website')
agent = Agent()

@app.route('/')
def index():
    return app.send_static_file('main.html')

# Serve static files (main.js, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/categories')
def get_categories():
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    return jsonify(categories)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    response = agent.handle(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=8080)