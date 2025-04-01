# DeepSeek Mental Health Support Chatbot - Technical Documentation

## Overview
The DeepSeek Mental Health Support Chatbot is a web-based application designed to provide empathetic mental health support through AI-powered conversations. Built with Flask and integrated with the Ollama API using the LLaMA2 model, the application offers a secure, user-friendly interface for mental health discussions and collects user feedback to improve responses.

## System Architecture

### Backend Components
1. **Flask Application (`app.py`)**
   - Handles HTTP routes and user authentication
   - Manages chat sessions and message history
   - Integrates with Ollama API for AI responses
   - Processes and stores user feedback

2. **Database Models**
   - User: Stores user authentication information
   - Chat: Manages chat sessions
   - Message: Stores individual messages and their feedback
   - Uses SQLite with SQLAlchemy ORM

3. **Authentication System**
   - Flask-Login for session management
   - Secure password hashing
   - Protected routes requiring authentication

### Frontend Components
1. **Chat Interface (`index.html`)**
   - Real-time message display
   - Message input system
   - Five-star feedback system for bot responses
   - Responsive design for various screen sizes

2. **Reviews Dashboard (`reviews.html`)**
   - Displays feedback statistics
   - Shows rated messages
   - Calculates average ratings
   - Visualizes rating distribution

## Key Features

### 1. User Authentication
- Registration with username/password
- Secure login system
- Session management
- Password hashing for security

### 2. Chat System
```python
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    # Get user message
    # Process through Ollama API
    # Store in database
    # Return bot response
```
- Real-time message processing
- Persistent message storage
- Error handling for API failures
- Message history preservation

### 3. Feedback System
```python
@app.route('/feedback', methods=['POST'])
@login_required
def feedback():
    # Get message rating
    # Update database
    # Process feedback
```
- Five-star rating system
- Immediate visual feedback
- Rating storage per message
- Statistical analysis

### 4. Reviews Dashboard
- Aggregate feedback display
- Rating distribution charts
- Average rating calculations
- Historical message review

## Data Flow

1. **User Input Flow**
   ```
   User Input → Flask Route → Ollama API → Database → User Interface
   ```

2. **Feedback Flow**
   ```
   User Rating → Flask Route → Database → Statistics Update → Reviews Dashboard
   ```

## API Integration

### Ollama API
```python
response = requests.post('http://localhost:11434/api/generate', 
    json={
        "model": "llama2",
        "prompt": f"You are a mental health support chatbot. Respond with empathy and understanding to the following message: {user_message}"
    })
```
- Local deployment
- LLaMA2 model optimization
- Empathetic response generation
- Error handling and retries

## Security Measures

1. **Authentication**
   - Password hashing using Werkzeug
   - Session-based authentication
   - CSRF protection
   - Secure cookie handling

2. **Data Protection**
   - SQLite database security
   - Input sanitization
   - XSS prevention
   - Rate limiting

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
```

### Chats Table
```sql
CREATE TABLE chats (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_bot BOOLEAN NOT NULL,
    timestamp DATETIME NOT NULL,
    rating INTEGER,
    FOREIGN KEY (chat_id) REFERENCES chats (id)
);
```

## Frontend Implementation

### Chat Interface
```javascript
// Message handling
function addMessage(content, type) {
    // Create message element
    // Add to chat container
    // Handle feedback if bot message
    // Scroll to bottom
}

// Feedback system
function submitFeedback(messageId, rating) {
    // Update UI
    // Send to server
    // Handle response
}
```

### Styling
- Modern, clean interface
- Responsive design
- Clear message distinction
- Intuitive feedback UI

## Development Setup

1. **Prerequisites**
   - Python 3.8+
   - Ollama API running locally
   - SQLite3

2. **Installation**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   - Configure Flask secret key
   - Set up database
   - Initialize Ollama API

4. **Running the Application**
   ```bash
   python app.py
   ```

## Testing

1. **Unit Tests**
   - Route testing
   - Authentication testing
   - API integration testing
   - Database operations testing

2. **Integration Tests**
   - End-to-end chat flow
   - Feedback system
   - User session handling

## Maintenance

1. **Database Maintenance**
   - Regular backups
   - Performance optimization
   - Data cleanup

2. **API Monitoring**
   - Response time tracking
   - Error rate monitoring
   - Usage statistics

## Future Enhancements

1. **Planned Features**
   - Multi-language support
   - Advanced analytics
   - User preference settings
   - Export chat history

2. **Technical Improvements**
   - WebSocket implementation
   - Caching system
   - Load balancing
   - API rate limiting

## Troubleshooting

### Common Issues
1. **API Connection**
   - Check Ollama service status
   - Verify network connectivity
   - Review API logs

2. **Database Issues**
   - Check permissions
   - Verify connections
   - Review SQL logs

3. **Authentication Problems**
   - Clear sessions
   - Reset user password
   - Check login logs

## Support

For technical support or contributions:
- GitHub: https://github.com/mffihri/mental-health-chatbot-MSc-Project
- Email: mffihri@gmail.com

## License
This project is licensed under the MIT License. See the LICENSE file for details.
