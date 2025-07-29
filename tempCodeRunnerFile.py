
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    response = agent.handle(data)
    return jsonify(response)
