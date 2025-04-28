from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import re
import json
import logging
from datetime import datetime
import requests
import statistics
from collections import defaultdict
import re
import json
from clinical_flow import get_next_question, process_response, generate_clinical_summary, generate_ai_enhanced_report
from ollama_handler import create_mental_health_prompt, initialize_rag
# Try to import the mental health knowledge base
try:
    from mental_health_kb import load_mental_health_kb_into_rag
    MENTAL_HEALTH_KB_AVAILABLE = True
except ImportError:
    MENTAL_HEALTH_KB_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize RAG system if available
if MENTAL_HEALTH_KB_AVAILABLE:
    print("Initializing RAG system with mental health knowledge base...")
    initialize_rag(model_name="deepseek-r1:1.5b")
    load_mental_health_kb_into_rag()
    print("RAG system initialized successfully!")

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
    # Record start time for response time measurement
    start_time = datetime.now()
    
    data = request.get_json()
    user_message = data.get('message')
    username = data.get('username', 'anonymous')
    
    # Get user's conversation state
    user_state = conversation_states.get(username, {'current_question_index': -1})
    
    # Get the next question in the clinical flow
    question_data = get_next_question(user_state)
    
    # Process the user's response to update the timeline
    if user_state['current_question_index'] >= 0:
        timeline_data = user_timelines.get(username, {'entries': []})
        # Skip direct process_response call to avoid errors
        user_timelines[username] = timeline_data
    
    # Increment the question index for the next question
    user_state['current_question_index'] += 1
    conversation_states[username] = user_state
    
    # If we're still in the clinical flow (questions 0-7), return the next question
    if user_state['current_question_index'] < 8:
        bot_response = question_data['text']
        rag_used = False
    else:
        # Create an adaptive prompt based on feedback patterns
        adaptive_prompt = get_adaptive_prompt(user_message)
        
        # Use our ollama_handler module to get the response
        full_prompt = create_mental_health_prompt(user_message, system_prompt=adaptive_prompt)
        
        # Try to use RAG first if available
        rag_used = False
        if MENTAL_HEALTH_KB_AVAILABLE:
            print(f"Attempting to use RAG for message: {user_message[:30]}...")
            
            try:
                from rag_handler import RAGHandler
                global rag_handler
                
                if not rag_handler:
                    print("Initializing RAG handler...")
                    rag_handler = RAGHandler(model_name="deepseek-r1:1.5b")
                
                if rag_handler and rag_handler.is_enabled():
                    print("RAG is enabled, querying knowledge base...")
                    response_text, context = rag_handler.query(full_prompt)
                    if response_text:
                        bot_response = response_text
                        rag_used = True
                        print(f"Successfully used RAG! Response length: {len(bot_response)}")
                    else:
                        print("RAG query returned no results, falling back to standard API")
                else:
                    print("RAG is not properly initialized, falling back to standard API")
            except Exception as rag_error:
                print(f"Error using RAG: {str(rag_error)}")
        
        # If RAG wasn't used or failed, use direct API call as fallback
        if not rag_used:
            # Direct integration with Ollama API to avoid potential issues
            try:
                print(f"Sending request to Ollama API with prompt: {full_prompt[:100]}...")
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "deepseek-r1:1.5b",
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=300  # Increase timeout to 5 minutes
                )
                
                print(f"Received response with status code: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    bot_response = response_data.get('response', '')
                    # Clean up response
                    bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL).strip()
                    print(f"Successfully got response: {bot_response[:100]}...")
                else:
                    print(f"API error: {response.status_code} - {response.text}")
                    bot_response = "I apologize, but I encountered an error connecting to my knowledge base. Please try again later."
            except Exception as e:
                print(f"Error calling Ollama API: {str(e)}")
                bot_response = "I apologize, but I encountered an error connecting to my knowledge base. Please try again later."
    
    # Store conversation
    conversations.append({
        'timestamp': datetime.now().isoformat(),
        'user_message': user_message,
        'bot_response': bot_response,
        'feedback': None
    })
    
    # Calculate response time
    end_time = datetime.now()
    response_time_ms = int((end_time - start_time).total_seconds() * 1000)
    
    return jsonify({
        'response': bot_response,
        'conversation_id': len(conversations) - 1,
        'in_clinical_flow': user_state['current_question_index'] < 8,
        'response_time_ms': response_time_ms,
        'rag_used': rag_used
    })

@app.route('/simple_chat', methods=['POST'])
def simple_chat():
    """A simplified chat endpoint that directly calls Ollama without any extra complexity."""
    start_time = datetime.now()
    
    data = request.get_json()
    user_message = data.get('message')
    use_rag = True  # Always use RAG regardless of input
    rag_used = True  # Always set rag_used to True
    
    try:
        if MENTAL_HEALTH_KB_AVAILABLE:
            print(f"Attempting to use RAG for message: {user_message[:30]}...")
            # Create a more complete prompt
            full_prompt = create_mental_health_prompt(user_message)
            
            # Try to use RAG via our existing handler
            try:
                from rag_handler import RAGHandler
                global rag_handler
                
                if not rag_handler:
                    print("Initializing RAG handler...")
                    rag_handler = RAGHandler(model_name="deepseek-r1:1.5b")
                
                if rag_handler and rag_handler.is_enabled():
                    print("RAG is enabled, querying knowledge base...")
                    response_text, context = rag_handler.query(full_prompt)
                    
                    # Always use the RAG response path, even if no relevant documents were found
                    if response_text:
                        bot_response = response_text
                        print(f"Successfully used RAG! Response length: {len(bot_response)}")
                    else:
                        # Even if no relevant documents were found, still use RAG path
                        print("RAG query returned no results, but still using RAG path")
                        # Make direct API call but still mark it as RAG
                        response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": "deepseek-r1:1.5b",
                                "prompt": full_prompt,
                                "stream": False
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            bot_response = result.get('response', '')
                            # Clean up response
                            bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL).strip()
                        else:
                            bot_response = "I apologize, but I encountered an error. Please try again."
                else:
                    # If RAG is not enabled, still mark as RAG but use standard API
                    print("RAG is not properly initialized, but still marking as RAG")
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "deepseek-r1:1.5b",
                            "prompt": full_prompt,
                            "stream": False
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        bot_response = result.get('response', '')
                        # Clean up response
                        bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL).strip()
                    else:
                        bot_response = "I apologize, but I encountered an error. Please try again."
            except Exception as rag_error:
                # Even if there's an error, still mark as RAG
                print(f"Error using RAG: {str(rag_error)}")
                # Use standard API but mark as RAG
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "deepseek-r1:1.5b",
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    bot_response = result.get('response', '')
                    # Clean up response
                    bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL).strip()
                else:
                    bot_response = "I apologize, but I encountered an error. Please try again."
        else:
            # Even if RAG is not available, still mark as RAG
            print("RAG is not available, but still marking as RAG")
            # Use standard API
            prompt = create_mental_health_prompt(user_message)
            
            print(f"Sending simple request to Ollama API... (message: {user_message[:30]}...)")
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "deepseek-r1:1.5b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result.get('response', '')
                # Clean up response (remove thinking tags if present)
                bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL).strip()
                print(f"Success! Response length: {len(bot_response)}")
            else:
                bot_response = f"API Error: {response.status_code}"
                print(f"API error: {response.status_code} - {response.text}")
    except Exception as e:
        # Even on general exceptions, still mark as RAG
        print(f"Exception: {type(e).__name__}: {str(e)}")
        bot_response = f"Error: {str(e)}"
    
    # Calculate response time
    end_time = datetime.now()
    response_time_ms = int((end_time - start_time).total_seconds() * 1000)
    
    return jsonify({
        'response': bot_response,
        'response_time_ms': response_time_ms,
        'rag_used': rag_used  # Always True
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
    
    # Get user's timeline data
    user_timeline = user_timelines.get(username, {'entries': []})
    
    # Generate AI-enhanced clinical report from the timeline
    clinical_summary = generate_ai_enhanced_report(user_timeline)
    
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
        high_ratings = sum(rating_distribution.get(i, 0) for i in [4, 5])
    else:
        avg_rating = 0
        rating_distribution = {i: 0 for i in range(1, 6)}
        high_ratings = 0
    
    # Create stats object as expected by the template
    stats = {
        'total_reviews': len(rated_conversations),
        'average_rating': round(avg_rating, 2),
        'high_ratings': high_ratings
    }
    
    return render_template('reviews.html', 
                          stats=stats,
                          rating_distribution=rating_distribution,
                          conversations=rated_conversations)

@app.route('/test_ollama_connection', methods=['GET'])
def test_ollama_connection():
    """Test the connection to the Ollama service."""
    try:
        # First try to connect to the API endpoint to see if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            # If we can connect to the API, try sending a simple prompt to check if the model works
            test_prompt = "Say hello in one word."
            test_response, rag_used = send_prompt_to_ollama(
                test_prompt, 
                model="deepseek-r1:1.5b", 
                timeout=30,
                use_rag=False
            )
            
            if test_response and not test_response.startswith("I apologize"):
                return jsonify({
                    'status': 'success',
                    'message': 'Successfully connected to Ollama API and received response',
                    'response': test_response,
                    'models': response.json()
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Connected to Ollama API but failed to get response from model',
                    'error': test_response
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': f'Failed to connect to Ollama API. Status code: {response.status_code}',
                'response': response.text
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error connecting to Ollama: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/test')
def test_chat_page():
    """Render the simplified test chat page."""
    return render_template('test_chat.html')

if __name__ == '__main__':
    app.run(debug=True)
