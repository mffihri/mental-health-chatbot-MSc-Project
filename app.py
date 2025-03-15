from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Ollama API endpoint (default running locally)
    response = requests.post('http://localhost:11434/api/generate',
                           json={
                               "model": "deepseek-coder",
                               "prompt": user_message,
                               "stream": False
                           })
    
    if response.status_code == 200:
        bot_response = response.json().get('response', '')
        return jsonify({'response': bot_response})
    else:
        return jsonify({'error': 'Failed to get response from Ollama'}), 500

if __name__ == '__main__':
    app.run(debug=True)
