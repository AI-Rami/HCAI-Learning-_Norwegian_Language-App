# HCAI Norwegian Language Learning App

A Human-Centered AI web application designed to help refugees learn basic Norwegian. This application provides an interactive platform for language learning with AI-powered dialogue practice and pronunciation feedback.

## 🎯 Features

- **Vocabulary Management**: Browse and learn Norwegian words with translations, pronunciation guides, and example sentences
- **Structured Lessons**: Progressive lessons organized by difficulty level and category
- **User Progress Tracking**: Track learning progress across lessons and vocabulary
- **AI Dialogue Practice**: Practice conversational Norwegian with AI-powered responses
- **Pronunciation Feedback**: Speech-to-text using OpenAI Whisper for pronunciation assessment
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **CORS Enabled**: Ready for React frontend integration

## 🏗️ Project Structure

```
HCAI-Learning-_Norwegian_Language-App/
├── main.py              # FastAPI application with all endpoints
├── database.py          # SQLAlchemy models and database setup
├── ai/
│   ├── __init__.py     # AI module initialization
│   ├── dialogue.py     # Norwegian dialogue AI
│   └── speech.py       # Whisper speech-to-text integration
├── seed_data.py        # Script to populate database with sample data
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AI-Rami/HCAI-Learning-_Norwegian_Language-App.git
cd HCAI-Learning-_Norwegian_Language-App
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Seed the database with sample data:
```bash
python seed_data.py
```

5. Run the API server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## 📚 API Endpoints

### Vocabulary Endpoints
- `GET /vocabulary` - Get all vocabulary words (with optional filters)
- `GET /vocabulary/{id}` - Get specific vocabulary word
- `POST /vocabulary` - Create new vocabulary word

### Lesson Endpoints
- `GET /lessons` - Get all lessons (with optional filters)
- `GET /lessons/{id}` - Get specific lesson
- `POST /lessons` - Create new lesson

### User Endpoints
- `GET /users` - Get all users
- `GET /users/{id}` - Get specific user
- `POST /users` - Create new user

### Progress Endpoints
- `GET /progress` - Get progress entries (with optional filters)
- `GET /progress/{id}` - Get specific progress entry
- `POST /progress` - Create progress entry
- `PUT /progress/{id}` - Update progress entry

### AI Dialogue Endpoints
- `POST /ai/dialogue` - Practice Norwegian dialogue with AI
- `POST /ai/dialogue/reset` - Reset conversation history
- `GET /ai/dialogue/topic/{category}` - Get practice topic by category

### AI Speech Endpoints
- `POST /ai/speech/transcribe` - Transcribe audio to text
- `POST /ai/speech/pronunciation` - Check pronunciation with feedback
- `GET /ai/speech/tips/{word}` - Get pronunciation tips for a word

### Utility Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check
- `GET /categories` - Get all available categories
- `GET /stats` - Get overall statistics

## 🤖 AI Integration

### Norwegian Dialogue Practice

The dialogue AI helps users practice conversational Norwegian:

```python
# Example request
POST /ai/dialogue
{
  "message": "Hei! Hvordan har du det?",
  "difficulty_level": "beginner"
}

# Response includes Norwegian text, English translation, and explanation
```

### Speech-to-Text Pronunciation Feedback

Uses OpenAI Whisper for accurate Norwegian speech recognition:

```python
# Example: Upload audio file for pronunciation check
POST /ai/speech/pronunciation
Form data:
  - expected_text: "Hei, hvordan har du det?"
  - audio: [audio file]

# Returns accuracy score, feedback, and improvement suggestions
```

## 🗄️ Database Schema

The application uses SQLite with the following main tables:

- **users**: User accounts and registration
- **vocabulary**: Norwegian words with translations and examples
- **lessons**: Learning content organized by difficulty
- **user_progress**: Track user learning progress

## 🌐 CORS Configuration

CORS is enabled for all origins by default. For production, update the allowed origins in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🛠️ Development

### Running Tests

```bash
# Add your test commands here
pytest
```

### Adding New Content

Use the admin endpoints to add new vocabulary and lessons, or modify `seed_data.py` to add more sample content.

## 📝 Configuration

### Environment Variables

You can set the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (for enhanced dialogue features)

### Whisper Model Size

The speech-to-text uses the "base" Whisper model by default. You can change this in `main.py`:

```python
speech_ai = WhisperSpeechToText(model_size="small")  # Options: tiny, base, small, medium, large
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Speech recognition powered by [OpenAI Whisper](https://github.com/openai/whisper)
- Designed to support refugees learning Norwegian

## 📧 Contact

For questions or support, please open an issue in the GitHub repository.