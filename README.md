# Mental Health Support Chatbot

An adaptive mental health support chatbot built with Flask and Ollama's LLaMA2 model. The chatbot learns from user feedback to provide more empathetic and effective responses over time.

## Features

### 1. Adaptive Learning System
- Learns from highly-rated responses (4-5 stars)
- Incorporates successful conversation patterns into future interactions
- Continuously improves response quality based on user feedback
- Maintains a database of effective response patterns

### 2. Interactive Chat Interface
- Clean, modern UI design
- Real-time response generation
- Two-step feedback system
- Visual feedback for user interactions
- Support for crisis situations with emergency contact information

### 3. Feedback and Reviews System
- Rate bot responses on emotional understanding (1-5 scale)
- Two-step feedback submission process
- Dedicated reviews page with statistics
- Track average ratings and high-performing responses
- Historical conversation view with ratings

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JavaScript
- **AI Model**: LLaMA2 via Ollama
- **Dependencies**: See requirements.txt

## Prerequisites

1. Python 3.x
2. Ollama installed with LLaMA2 model
3. Git (for version control)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mffihri/mental-health-chatbot-MSc-Project.git
cd mental-health-chatbot-MSc-Project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Ollama and pull the LLaMA2 model:
- Download Ollama from [ollama.ai](https://ollama.ai)
- Run: `ollama pull llama2`

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Start chatting with the bot and provide feedback on responses

4. View feedback statistics at:
```
http://localhost:5000/reviews
```

## Project Structure

```
mental-health-chatbot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Chat interface
│   └── reviews.html      # Feedback review page
└── README.md             # Project documentation
```

## Features in Detail

### Adaptive Learning
The chatbot uses a sophisticated learning system that:
- Stores successful conversation patterns
- Tracks average ratings for different response types
- Incorporates highly-rated responses into future prompts
- Adapts its communication style based on user feedback

### Feedback System
Users can:
- Rate how well the bot understood their emotional state
- Preview their rating before submission
- Submit feedback with a dedicated button
- View all feedback and statistics on the reviews page

### Reviews Dashboard
Provides:
- Average rating across all conversations
- Total number of reviews
- Count of high ratings (4-5 stars)
- Detailed conversation history with ratings

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Important Note

This chatbot is designed for general emotional support and is not a replacement for professional mental health services. If you're experiencing a crisis, please contact professional mental health services or call 988 (US) for immediate support.
