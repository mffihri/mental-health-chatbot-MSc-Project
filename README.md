# RAG-Enhanced Mental Health Chatbot

A mental health support chatbot built with Flask and Ollama, enhanced by Retrieval Augmented Generation (RAG) for more informed and supportive responses.

## Features

- Real-time chat interface with modern UI
- RAG-powered responses using a curated mental health knowledge base
- Feedback and reviews system for user experience
- API documented in `API_REFERENCE.md`

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JavaScript
- **AI Model**: LLaMA2 via Ollama
- **RAG & Embeddings**: LangChain, sentence-transformers, scikit-learn, numpy, pytorch
- **Dependencies**: See requirements.txt

## Prerequisites

1. Python 3.x
2. Ollama installed with LLaMA2 model
3. Git (for version control)
4. RAG dependencies (see requirements.txt)

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
- Run:
```bash
ollama pull llama2
```

5. For RAG: Ensure all dependencies in requirements.txt are installed (including sentence-transformers, scikit-learn, numpy, torch, langchain)

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```bash
http://localhost:5000
```

3. Start chatting with the bot and provide feedback on responses

4. View feedback statistics at:
```bash
http://localhost:5000/reviews
```

## API Reference

A comprehensive API reference is available in [API_REFERENCE.md](./API_REFERENCE.md).

## Project Structure

```
mental-health-chatbot-MSc-Project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── rag_handler.py         # RAG logic
├── mental_health_kb.py    # Knowledge base
├── templates/
│   ├── index.html        # Chat interface
│   └── reviews.html      # Feedback review page
├── LICENSE               # MIT License
├── README.md             # Project documentation
├── API_REFERENCE.md      # API documentation
└── ...
```

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
