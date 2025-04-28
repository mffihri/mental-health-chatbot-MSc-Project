# DeepSeek Mental Health Chatbot API Reference

## Core Endpoints

### 1. Main Chat Endpoint

**Endpoint:** `POST /chat`  
**Purpose:** Primary conversation interface with clinical flow integration and RAG enhancement

**Request:**
```json
{
  "message": "I've been feeling anxious lately",
  "username": "user123"  // Optional, defaults to "anonymous"
}
```

**Response:**
```json
{
  "response": "I understand that you've been experiencing anxiety recently. Can you tell me more about when these feelings occur and how they affect your daily life?",
  "conversation_id": 42,
  "in_clinical_flow": true,
  "response_time_ms": 2541,
  "rag_used": true
}
```

**Notes:**
- Tracks conversation state through user sessions
- Implements RAG for knowledge-enhanced responses
- Handles clinical assessment flow for new conversations

### 2. Simplified Chat Endpoint

**Endpoint:** `POST /simple_chat`  
**Purpose:** Streamlined interface for testing RAG functionality

**Request:**
```json
{
  "message": "What is depression?",
  "use_rag": true  // Optional, defaults to true
}
```

**Response:**
```json
{
  "response": "Depression is a mood disorder characterized by persistent feelings of sadness, hopelessness, and loss of interest in activities once enjoyed. Common symptoms include...",
  "response_time_ms": 3214,
  "rag_used": true
}
```

**Notes:**
- Bypasses clinical flow for direct question-answering
- Explicit flag to control RAG usage
- Used by the `/test` interface

### 3. Feedback Collection

**Endpoint:** `POST /feedback`  
**Purpose:** Record user evaluations of bot responses

**Request:**
```json
{
  "conversation_id": 42,
  "rating": "positive",
  "comment": "This response was very helpful"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Thank you for your feedback!"
}
```

**Notes:**
- Supports basic positive/negative ratings
- Optional comments for qualitative feedback
- Data used to adapt future responses

### 4. Diagnostic Connection Test

**Endpoint:** `GET /test_ollama_connection`  
**Purpose:** Verify connectivity to Ollama API

**Request:** No body required (GET request)

**Response:**
```json
{
  "status": "success",
  "message": "Successfully connected to Ollama API",
  "model": "deepseek-r1:1.5b",
  "version": "1.0.0"
}
```

**Notes:**
- Returns detailed diagnostics if connection fails
- Verifies model availability and version

### 5. Test Interface

**Endpoint:** `GET /test`  
**Purpose:** Render simplified test chat interface

**Request:** No body required (GET request)

**Response:** HTML page with test chat interface

**Notes:**
- Provides alternate UI for testing RAG functionality
- Uses `/simple_chat` endpoint for backend communication

## Response Objects

### Chat Response

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | Bot's response text, may include Markdown formatting |
| `conversation_id` | integer | Unique identifier for tracking conversation |
| `in_clinical_flow` | boolean | Whether response is part of structured assessment |
| `response_time_ms` | integer | Processing time in milliseconds |
| `rag_used` | boolean | Whether response was enhanced with knowledge base |

### Error Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always "error" for error responses |
| `message` | string | Human-readable error description |
| `error_code` | string | Optional machine-readable error code |

## Authentication

The current implementation uses simple session-based authentication. Future versions will implement token-based authentication with the following endpoints:

- `POST /login`: Authenticate existing user
- `POST /register`: Create new user account
- `POST /logout`: End authenticated session

## Testing Examples

**cURL Request (Chat):**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How can mindfulness help with anxiety?", "username": "testuser"}'
```

**Python Request (with RAG):**
```python
import requests
response = requests.post(
    "http://localhost:5000/simple_chat",
    json={"message": "What are effective coping strategies for depression?", "use_rag": True}
)
print(response.json())
```

## Data Models

### Timeline Entry Model
```json
{
  "question": "What brings you here today?",
  "response": "I've been feeling overwhelmed at work",
  "category": "presenting_problems",
  "timestamp": "2025-04-28T07:15:42+01:00"
}
```

### Conversation Message Model
```json
{
  "sender": "bot",
  "message": "I understand that work has been difficult lately...",
  "timestamp": "2025-04-28T07:16:12+01:00",
  "conversation_id": "conv-12345",
  "message_id": "msg-67890",
  "in_clinical_flow": true,
  "clinical_flow_index": 2
}
```

### Feedback Model
```json
{
  "rating": "positive",
  "comment": "This was exactly what I needed to hear",
  "timestamp": "2025-04-28T07:18:30+01:00"
}
```
