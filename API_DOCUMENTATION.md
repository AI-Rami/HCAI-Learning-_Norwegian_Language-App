# Norwegian Language Learning API - Complete Documentation

## Overview

This is a comprehensive FastAPI backend for a Human-Centered AI web application designed to help refugees learn basic Norwegian. The API provides vocabulary management, structured lessons, user progress tracking, and AI-powered features including dialogue practice and pronunciation feedback.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, you should implement JWT tokens or OAuth2.

## Response Format

All responses are in JSON format. Successful responses return appropriate HTTP status codes (200, 201) along with the requested data. Errors return 4xx or 5xx status codes with error details.

---

## API Endpoints

### Root & Health

#### GET `/`
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "Welcome to Norwegian Language Learning API",
  "version": "1.0.0",
  "endpoints": {
    "vocabulary": "/vocabulary",
    "lessons": "/lessons",
    "users": "/users",
    "progress": "/progress",
    "dialogue": "/ai/dialogue",
    "speech": "/ai/speech"
  }
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-04T06:47:19.183147"
}
```

---

## Vocabulary Endpoints

### GET `/vocabulary`
Get all vocabulary words with optional filtering.

**Query Parameters:**
- `category` (optional): Filter by category (e.g., "greetings", "healthcare")
- `difficulty_level` (optional): Filter by difficulty (1-3)
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Number of records to return (default: 100, max: 100)

**Example:**
```bash
GET /vocabulary?category=greetings&limit=5
```

**Response:**
```json
[
  {
    "id": 1,
    "norwegian_word": "Hei",
    "english_translation": "Hi/Hello",
    "category": "greetings",
    "difficulty_level": 1,
    "pronunciation_guide": "hey",
    "example_sentence": "Hei, hvordan har du det?"
  }
]
```

### GET `/vocabulary/{vocabulary_id}`
Get a specific vocabulary word by ID.

**Response:** Single vocabulary object (same structure as above)

### POST `/vocabulary`
Create a new vocabulary word.

**Request Body:**
```json
{
  "norwegian_word": "Buss",
  "english_translation": "Bus",
  "category": "transportation",
  "difficulty_level": 1,
  "pronunciation_guide": "boos",
  "example_sentence": "Bussen kommer snart."
}
```

**Response:** Created vocabulary object with status code 201

---

## Lesson Endpoints

### GET `/lessons`
Get all lessons with optional filtering.

**Query Parameters:**
- `category` (optional): Filter by category
- `difficulty_level` (optional): Filter by difficulty (1-3)
- `skip` (optional): Pagination offset
- `limit` (optional): Number of records (max: 100)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Introduction to Norwegian Greetings",
    "description": "Learn basic Norwegian greetings",
    "difficulty_level": 1,
    "content": "Lesson content here...",
    "category": "greetings",
    "created_at": "2025-10-04T06:47:19.183147"
  }
]
```

### GET `/lessons/{lesson_id}`
Get a specific lesson by ID.

### POST `/lessons`
Create a new lesson.

**Request Body:**
```json
{
  "title": "Daily Conversations",
  "description": "Practice everyday Norwegian conversations",
  "difficulty_level": 2,
  "content": "Detailed lesson content...",
  "category": "daily_life"
}
```

---

## User Endpoints

### GET `/users`
Get all users.

**Query Parameters:**
- `skip`, `limit` for pagination

**Response:**
```json
[
  {
    "id": 1,
    "username": "demo_user",
    "created_at": "2025-10-04T06:47:19.184128"
  }
]
```

### GET `/users/{user_id}`
Get a specific user by ID.

### POST `/users`
Create a new user.

**Request Body:**
```json
{
  "username": "new_learner"
}
```

**Note:** Username must be unique. Returns 400 if username exists.

---

## Progress Endpoints

### GET `/progress`
Get user progress entries with optional filtering.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `lesson_id` (optional): Filter by lesson
- `skip`, `limit` for pagination

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "lesson_id": 1,
    "vocabulary_id": null,
    "completed": 1,
    "score": 85.5,
    "last_accessed": "2025-10-04T06:47:19.183147"
  }
]
```

**Completion Status:**
- 0 = Not started
- 1 = In progress
- 2 = Completed

### GET `/progress/{progress_id}`
Get a specific progress entry by ID.

### POST `/progress`
Create a new progress entry.

**Request Body:**
```json
{
  "user_id": 1,
  "lesson_id": 1,
  "vocabulary_id": null,
  "completed": 1,
  "score": 85.5
}
```

### PUT `/progress/{progress_id}`
Update an existing progress entry.

**Request Body:**
```json
{
  "completed": 2,
  "score": 95.0
}
```

---

## AI Dialogue Endpoints

### POST `/ai/dialogue`
Practice Norwegian dialogue with AI.

**Request Body:**
```json
{
  "message": "Hei! Jeg heter John.",
  "difficulty_level": "beginner"
}
```

**Difficulty Levels:** `beginner`, `intermediate`, `advanced`

**Response:**
```json
{
  "norwegian": "Hei! Hvordan har du det?",
  "english": "Hi! How are you?",
  "explanation": "'Hvordan har du det?' is a common greeting"
}
```

### POST `/ai/dialogue/reset`
Reset conversation history to start fresh.

**Response:**
```json
{
  "message": "Conversation history reset"
}
```

### GET `/ai/dialogue/topic/{category}`
Get a practice dialogue topic by category.

**Categories:** `greetings`, `shopping`, `healthcare`, `daily_life`

**Response:**
```json
{
  "scenario": "Practice shopping at a Norwegian store",
  "starters": [
    "Hvor mye koster dette? (How much does this cost?)",
    "Jeg leter etter... (I'm looking for...)"
  ]
}
```

---

## AI Speech Endpoints

### POST `/ai/speech/transcribe`
Transcribe audio to text using Whisper.

**Request:** Multipart form-data with audio file

**Example:**
```bash
curl -X POST http://localhost:8000/ai/speech/transcribe \
  -F "audio=@recording.wav"
```

**Response:**
```json
{
  "text": "Hei, hvordan har du det?",
  "language": "no",
  "confidence": 0.95
}
```

### POST `/ai/speech/pronunciation`
Check pronunciation by comparing audio with expected text.

**Request:** Multipart form-data
- `expected_text`: The correct Norwegian text
- `audio`: Audio file to check

**Response:**
```json
{
  "accuracy": 87.5,
  "feedback": "Good job! Your pronunciation is clear",
  "suggestions": [
    {
      "word": "hvordan",
      "tip": "Practice pronouncing 'hvordan' more clearly"
    }
  ],
  "expected": "Hei, hvordan har du det?",
  "heard": "Hei, vordan har du det?"
}
```

### GET `/ai/speech/tips/{word}`
Get pronunciation tips for a Norwegian word.

**Response:**
```json
{
  "word": "god morgen",
  "tips": [
    "Practice this word slowly, focusing on each syllable"
  ],
  "ipa": "[IPA notation for 'god morgen']"
}
```

---

## Utility Endpoints

### GET `/categories`
Get all available categories.

**Response:**
```json
{
  "categories": ["greetings", "daily_life", "healthcare", "shopping"],
  "vocabulary_categories": ["greetings", "daily_life", "healthcare"],
  "lesson_categories": ["greetings", "daily_life", "shopping"]
}
```

### GET `/stats`
Get overall statistics.

**Response:**
```json
{
  "total_users": 4,
  "total_vocabulary": 13,
  "total_lessons": 4,
  "total_progress_entries": 3
}
```

---

## Error Responses

### 400 Bad Request
Invalid request data or duplicate resource.

```json
{
  "detail": "Username already exists"
}
```

### 404 Not Found
Resource not found.

```json
{
  "detail": "Vocabulary not found"
}
```

### 500 Internal Server Error
Server error.

```json
{
  "detail": "Transcription failed: [error details]"
}
```

---

## Data Models

### Vocabulary
```typescript
{
  id: number
  norwegian_word: string
  english_translation: string
  category: string
  difficulty_level: number (1-3)
  pronunciation_guide?: string
  example_sentence?: string
}
```

### Lesson
```typescript
{
  id: number
  title: string
  description: string
  difficulty_level: number (1-3)
  content: string
  category: string
  created_at: datetime
}
```

### User
```typescript
{
  id: number
  username: string
  created_at: datetime
}
```

### UserProgress
```typescript
{
  id: number
  user_id: number
  lesson_id: number
  vocabulary_id?: number
  completed: number (0=not started, 1=in progress, 2=completed)
  score: number
  last_accessed: datetime
}
```

---

## Testing

### Interactive API Documentation
Visit http://localhost:8000/docs for Swagger UI with interactive testing.

### Example Usage Script
Run the provided example script:
```bash
python example_usage.py
```

### cURL Examples

**Get vocabulary:**
```bash
curl http://localhost:8000/vocabulary?category=greetings
```

**Create user:**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"learner1"}'
```

**Practice dialogue:**
```bash
curl -X POST http://localhost:8000/ai/dialogue \
  -H "Content-Type: application/json" \
  -d '{"message":"Hei","difficulty_level":"beginner"}'
```

---

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production deployment using libraries like `slowapi`.

## CORS

CORS is enabled for all origins. For production, update in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Deployment

1. **Database**: Upgrade from SQLite to PostgreSQL or MySQL
2. **Environment Variables**: Use `.env` file for sensitive data
3. **HTTPS**: Deploy behind reverse proxy (nginx) with SSL
4. **Authentication**: Implement JWT or OAuth2
5. **Rate Limiting**: Add rate limiting middleware
6. **Logging**: Configure proper logging (not just console)
7. **Monitoring**: Add health checks and monitoring

---

## Support

For issues or questions, please refer to the README.md or open an issue in the GitHub repository.
