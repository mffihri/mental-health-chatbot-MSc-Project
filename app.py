from flask import Flask, request, jsonify, render_template
import requests
import json
from datetime import datetime
from collections import defaultdict
import statistics

app = Flask(__name__)

# Store conversation history and feedback
conversations = []

# Store learned patterns from highly-rated conversations
learned_patterns = {
    'successful_responses': [],  # Store responses that received high ratings
    'avg_ratings': defaultdict(list),  # Track average ratings for different response patterns
}

def update_learned_patterns(conversation, rating):
    if rating >= 4:  # Consider responses with ratings of 4 or 5 as successful
        learned_patterns['successful_responses'].append({
            'user_message': conversation['user_message'],
            'bot_response': conversation['bot_response'],
            'rating': rating
        })
        
    # Update average ratings
    response_key = hash(conversation['bot_response'])  # Simple way to identify similar responses
    learned_patterns['avg_ratings'][response_key].append(rating)

def get_adaptive_prompt(user_message):
    base_prompt = """You are a compassionate mental health support chatbot. Your role is to:
    1. Listen empathetically to users
    2. Identify and acknowledge their emotional state
    3. Provide supportive responses
    4. Ask about their feelings and experiences
    5. Suggest healthy coping strategies when appropriate
    
    Important: Always maintain a supportive, non-judgmental tone. If you detect signs of serious distress or crisis, 
    recommend professional help and provide crisis hotline numbers."""

    # Add successful patterns if available
    if learned_patterns['successful_responses']:
        # Find the top 3 most successful responses
        top_responses = sorted(
            learned_patterns['successful_responses'],
            key=lambda x: x['rating'],
            reverse=True
        )[:3]
        
        examples = "\n\nHere are examples of highly effective responses:\n"
        for resp in top_responses:
            examples += f"\nUser: {resp['user_message']}\nEffective Response: {resp['bot_response']}\n"
        
        base_prompt += examples

    base_prompt += "\n\nAfter your response, ask the user to rate how well you understood their emotional state on a scale of 1-5."
    return base_prompt

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/reviews')
def reviews():
    # Format conversations for display
    formatted_conversations = []
    for idx, conv in enumerate(conversations):
        if conv['feedback'] is not None:  # Only show conversations with feedback
            formatted_conversations.append({
                'id': idx,
                'timestamp': datetime.fromisoformat(conv['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                'user_message': conv['user_message'],
                'bot_response': conv['bot_response'],
                'feedback': conv['feedback']
            })
    
    # Calculate statistics
    if formatted_conversations:
        ratings = [conv['feedback'] for conv in formatted_conversations]
        stats = {
            'average_rating': round(statistics.mean(ratings), 2),
            'total_reviews': len(ratings),
            'high_ratings': len([r for r in ratings if r >= 4]),
        }
    else:
        stats = {
            'average_rating': 0,
            'total_reviews': 0,
            'high_ratings': 0,
        }
    
    return render_template('reviews.html', conversations=formatted_conversations, stats=stats)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Get adaptive prompt based on learned patterns
    system_prompt = get_adaptive_prompt(user_message)
    full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
    
    # Ollama API call with llama2 model
    response = requests.post('http://localhost:11434/api/generate',
                           json={
                               "model": "llama2",
                               "prompt": full_prompt,
                               "stream": False
                           })
    
    if response.status_code == 200:
        bot_response = response.json().get('response', '')
        
        # Store conversation
        conversations.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response,
            'feedback': None
        })
        
        return jsonify({
            'response': bot_response,
            'conversation_id': len(conversations) - 1
        })
    else:
        return jsonify({'error': 'Failed to get response from Ollama'}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    conversation_id = data.get('conversation_id')
    rating = data.get('rating')
    
    if conversation_id is not None and 0 <= conversation_id < len(conversations):
        conversations[conversation_id]['feedback'] = rating
        # Update learned patterns with the new feedback
        update_learned_patterns(conversations[conversation_id], rating)
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Invalid conversation ID'}), 400

if __name__ == '__main__':
    app.run(debug=True)
