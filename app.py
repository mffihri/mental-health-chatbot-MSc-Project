from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
import os
from datetime import datetime
from collections import defaultdict
import statistics
import re
import json
from clinical_flow import get_next_question, process_response, generate_clinical_summary

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# In-memory storage for users, conversations, and feedback
users = {}
conversations = []
user_timelines = {}  # Store clinical assessment timelines by user ID
conversation_states = {}  # Track conversation state for clinical flow

# Adaptive learning: Store feedback patterns
feedback_patterns = defaultdict(list)

def get_adaptive_prompt(user_message):
    """Generate an adaptive prompt based on learned patterns"""
    if not feedback_patterns:
        return "You are a mental health support chatbot. Respond with empathy and understanding."
    
    # Find patterns with positive feedback
    positive_patterns = [pattern for pattern, ratings in feedback_patterns.items() 
                        if ratings and statistics.mean(ratings) >= 4]
    
    if positive_patterns:
        return "You are a mental health support chatbot. Based on user feedback, please emphasize: " + ", ".join(positive_patterns)
    
    return "You are a mental health support chatbot. Respond with empathy and understanding."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            # Initialize user timeline if not exists
            if username not in user_timelines:
                user_timelines[username] = {'entries': []}
            
            # Initialize conversation state if not exists
            if username not in conversation_states:
                conversation_states[username] = {'current_question_index': -1}
                
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        if username in users:
            flash('Username already exists')
            return render_template('register.html')
        
        users[username] = {'password': password}
        
        # Initialize user timeline
        user_timelines[username] = {'entries': []}
        
        # Initialize conversation state
        conversation_states[username] = {'current_question_index': -1}
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    username = data.get('username', 'anonymous')
    
    # Get user's conversation state
    user_state = conversation_states.get(username, {'current_question_index': -1})
    
    # Get the next question in the clinical flow
    question_data = get_next_question(user_state)
    
    # Process the user's response to update the timeline
    if user_state['current_question_index'] >= 0:  # Skip for the first interaction
        user_timeline = user_timelines.get(username, {'entries': []})
        previous_question = get_next_question({'current_question_index': user_state['current_question_index'] - 1})
        user_timeline = process_response(user_message, previous_question, user_timeline)
        user_timelines[username] = user_timeline
    
    # Update the conversation state to move to the next question
    user_state['current_question_index'] += 1
    conversation_states[username] = user_state
    
    # If we're in the guided clinical flow (first 8 interactions)
    if user_state['current_question_index'] < 8:
        bot_response = question_data['text']
    else:
        # After the clinical flow, use the AI model for responses
        system_prompt = get_adaptive_prompt(user_message)
        full_prompt = f"""You are a compassionate and trauma-informed mental health AI assistant designed to support users while integrating clinical psychology data. Your role is to help users process their emotions, provide evidence-based coping strategies, and recognize trauma-related patterns while ensuring ethical and sensitive interactions. Your core functions include:

Clinical Data Integration:
- Utilize anonymized psychological data to generate user conversation histories or timelines in compliance with GDPR.
- Offer structured insights into mental health progress while maintaining strict confidentiality.

Trauma and Risk Detection:
- Identify signs of adverse childhood experiences (ACEs), trauma, heightened suicide risk, and substance abuse.
- Provide non-intrusive, supportive prompts to encourage users to seek professional help when necessary.
- Offer clinicians structured summaries of risks without making definitive diagnoses.

Trauma-Informed Care:
- Approach users with empathy, recognizing the impact of past trauma on present behavior.
- Offer guidance on physical health, integrated mental health services, and pharmacological interventions where appropriate.
- Provide practical coping mechanisms grounded in Cognitive Behavioral Therapy (CBT), Dialectical Behavior Therapy (DBT), and mindfulness techniques.

Ethical and User-Centered Approach:
- Prioritize user safety by following crisis intervention protocols.
- Encourage professional consultation for severe mental health concerns.
- Ensure users feel heard and respected, reinforcing autonomy in their healing journey.

Your responses should be warm, evidence-based, and adaptable to different emotional states. Always validate the user's feelings and guide them toward self-reflection and professional resources where necessary.

Respond with empathy and understanding to the following message: {user_message}"""
        
        # Ollama API call with DeepSeek-R1 1.5B model
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": "deepseek-r1:1.5b",
                                   "prompt": full_prompt,
                                   "stream": False
                               })
        
        if response.status_code == 200:
            bot_response = response.json().get('response', '')
            
            # Remove content between <think> and </think> tags
            bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL)
            bot_response = bot_response.strip()
        else:
            bot_response = "I apologize, but I encountered an error. Please try again."
    
    # Store conversation
    conversations.append({
        'timestamp': datetime.now().isoformat(),
        'user_message': user_message,
        'bot_response': bot_response,
        'feedback': None
    })
    
    return jsonify({
        'response': bot_response,
        'conversation_id': len(conversations) - 1,
        'in_clinical_flow': user_state['current_question_index'] < 8
    })

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    rating = data.get('rating')
    
    if conversation_id is not None and rating is not None:
        if 0 <= conversation_id < len(conversations):
            conversations[conversation_id]['feedback'] = rating
            
            # Extract keywords for adaptive learning
            user_message = conversations[conversation_id]['user_message']
            bot_response = conversations[conversation_id]['bot_response']
            
            # Simple keyword extraction (in a real app, use NLP)
            keywords = ['empathy', 'advice', 'resources', 'validation', 'coping']
            for keyword in keywords:
                if keyword in bot_response.lower():
                    feedback_patterns[keyword].append(rating)
            
            return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid feedback data'}), 400

@app.route('/timeline', methods=['GET'])
def view_timeline():
    username = request.args.get('username', 'anonymous')
    
    # Generate clinical summary from the timeline
    user_timeline = user_timelines.get(username, {'entries': []})
    clinical_summary = generate_clinical_summary(user_timeline)
    
    return render_template('timeline.html', 
                          timeline=user_timeline,
                          clinical_summary=clinical_summary)

@app.route('/reviews')
def reviews():
    # Calculate feedback statistics
    rated_conversations = [conv for conv in conversations if conv['feedback'] is not None]
    
    if rated_conversations:
        avg_rating = sum(conv['feedback'] for conv in rated_conversations) / len(rated_conversations)
        rating_distribution = {i: len([conv for conv in rated_conversations if conv['feedback'] == i]) for i in range(1, 6)}
    else:
        avg_rating = 0
        rating_distribution = {i: 0 for i in range(1, 6)}
    
    return render_template('reviews.html', 
                         total_ratings=len(rated_conversations),
                         avg_rating=round(avg_rating, 2),
                         rating_distribution=rating_distribution,
                         conversations=rated_conversations)

if __name__ == '__main__':
    app.run(debug=True)
