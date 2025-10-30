"""
FastAPI Backend for Norwegian Language Learning App
Uses OpenAI Whisper API and GPT-3.5-turbo for AI features.
"""

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from database import (
    init_db, get_db, User, Vocabulary, Lesson, UserProgress
)
from ai.dialogue import NorwegianDialogueAI
from ai.speech import WhisperSpeechToText


# ============================================================
# 🧩 Pydantic Models
# ============================================================

class VocabularyCreate(BaseModel):
    norwegian_word: str
    english_translation: str
    category: str
    difficulty_level: int
    pronunciation_guide: Optional[str] = None
    example_sentence: Optional[str] = None


class VocabularyResponse(BaseModel):
    id: int
    norwegian_word: str
    english_translation: str
    category: str
    difficulty_level: int
    pronunciation_guide: Optional[str]
    example_sentence: Optional[str]

    class Config:
        from_attributes = True


class LessonCreate(BaseModel):
    title: str
    description: str
    difficulty_level: int
    content: str
    category: str


class LessonResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty_level: int
    content: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProgressCreate(BaseModel):
    user_id: int
    lesson_id: int
    vocabulary_id: Optional[int] = None
    completed: int = 0
    score: float = 0.0


class ProgressUpdate(BaseModel):
    completed: Optional[int] = None
    score: Optional[float] = None


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    vocabulary_id: Optional[int]
    completed: int
    score: float
    last_accessed: datetime

    class Config:
        from_attributes = True


class DialogueRequest(BaseModel):
    message: str
    difficulty_level: str = "beginner"


class DialogueResponse(BaseModel):
    norwegian: str
    english: str
    explanation: str


class PronunciationFeedback(BaseModel):
    accuracy: float
    feedback: str
    suggestions: List[dict]
    expected: str
    heard: str


# ============================================================
# ⚙️ FastAPI Setup
# ============================================================

app = FastAPI(
    title="Norwegian Language Learning API",
    description="API for learning Norwegian with AI support (GPT + Whisper).",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI modules
dialogue_ai = None
speech_ai = None


@app.on_event("startup")
def startup_event():
    """Initialize database and AI models when the app starts."""
    global dialogue_ai, speech_ai
    init_db()
    dialogue_ai = NorwegianDialogueAI()
    speech_ai = WhisperSpeechToText()


# ============================================================
# 📖 Root & Health Check
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Norwegian Learning API",
        "version": "1.1.0",
        "endpoints": {
            "vocabulary": "/vocabulary",
            "lessons": "/lessons",
            "users": "/users",
            "progress": "/progress",
            "dialogue": "/ai/dialogue",
            "speech": "/ai/speech"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ============================================================
# 📚 Vocabulary Endpoints
# ============================================================

@app.get("/vocabulary", response_model=List[VocabularyResponse])
def get_vocabulary(
    category: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Vocabulary)
    if category:
        query = query.filter(Vocabulary.category == category)
    if difficulty_level:
        query = query.filter(Vocabulary.difficulty_level == difficulty_level)
    return query.offset(skip).limit(limit).all()


@app.get("/vocabulary/{vocabulary_id}", response_model=VocabularyResponse)
def get_vocabulary_by_id(vocabulary_id: int, db: Session = Depends(get_db)):
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    return vocab


@app.post("/vocabulary", response_model=VocabularyResponse, status_code=201)
def create_vocabulary(vocabulary: VocabularyCreate, db: Session = Depends(get_db)):
    db_vocabulary = Vocabulary(**vocabulary.dict())
    db.add(db_vocabulary)
    db.commit()
    db.refresh(db_vocabulary)
    return db_vocabulary


@app.put("/vocabulary/{vocabulary_id}", response_model=VocabularyResponse)
def update_vocabulary(vocabulary_id: int, updated_data: dict = Body(...), db: Session = Depends(get_db)):
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    for key, value in updated_data.items():
        if hasattr(vocab, key) and value is not None:
            setattr(vocab, key, value)
    db.commit()
    db.refresh(vocab)
    return vocab


@app.delete("/vocabulary/{vocabulary_id}")
def delete_vocabulary(vocabulary_id: int, db: Session = Depends(get_db)):
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    db.delete(vocab)
    db.commit()
    return {"message": f"Vocabulary item {vocabulary_id} deleted successfully"}


# ============================================================
# 🎓 Lessons Endpoints
# ============================================================

@app.get("/lessons", response_model=List[LessonResponse])
def get_lessons(
    category: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Lesson)
    if category:
        query = query.filter(Lesson.category == category)
    if difficulty_level:
        query = query.filter(Lesson.difficulty_level == difficulty_level)
    return query.offset(skip).limit(limit).all()


@app.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson_by_id(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@app.post("/lessons", response_model=LessonResponse, status_code=201)
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db)):
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


# ============================================================
# 👤 Users Endpoints
# ============================================================

@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ============================================================
# 📊 Progress Endpoints
# ============================================================

@app.get("/progress", response_model=List[ProgressResponse])
def get_all_progress(
    user_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(UserProgress)
    if user_id:
        query = query.filter(UserProgress.user_id == user_id)
    if lesson_id:
        query = query.filter(UserProgress.lesson_id == lesson_id)
    return query.offset(skip).limit(limit).all()


@app.put("/progress/{progress_id}", response_model=ProgressResponse)
def update_progress(progress_id: int, progress_update: ProgressUpdate, db: Session = Depends(get_db)):
    db_progress = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if not db_progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    if progress_update.completed is not None:
        db_progress.completed = progress_update.completed
    if progress_update.score is not None:
        db_progress.score = progress_update.score
    db_progress.last_accessed = datetime.utcnow()
    db.commit()
    db.refresh(db_progress)
    return db_progress


# ============================================================
# 💬 AI Dialogue Endpoints
# ============================================================

@app.post("/ai/dialogue", response_model=DialogueResponse)
def practice_dialogue(request: DialogueRequest):
    """Generate an AI tutor response with memory (multi-turn chat)."""
    global dialogue_ai
    reply = dialogue_ai.generate_response(
        user_message=request.message,
        difficulty=request.difficulty_level
    )

    # Split Norwegian and English lines
    if "\n" in reply:
        parts = reply.split("\n", 1)
        norwegian = parts[0].strip()
        english = parts[1].strip()
    else:
        norwegian, english = reply, ""

    return {
        "norwegian": norwegian,
        "english": english,
        "explanation": "AI-generated Norwegian and English reply."
    }


@app.post("/ai/dialogue/reset")
def reset_dialogue():
    """Clear chat history for current AI session."""
    global dialogue_ai
    dialogue_ai.reset()
    return {"message": "✅ Chat history cleared."}


# ============================================================
# 🎙️ Speech & Pronunciation Endpoints
# ============================================================

@app.post("/ai/speech/transcribe")
async def transcribe_speech(audio: UploadFile = File(...)):
    global speech_ai
    try:
        temp_audio_path = f"temp_{audio.filename}"
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())
        result = speech_ai.transcribe_audio(temp_audio_path)
        import os
        os.remove(temp_audio_path)
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/ai/speech/pronunciation", response_model=PronunciationFeedback)
async def check_pronunciation(expected_text: str = Form(...), audio: UploadFile = File(...)):
    global speech_ai
    try:
        temp_audio_path = f"temp_{audio.filename}"
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())
        transcribed_text = speech_ai.transcribe_audio(temp_audio_path)
        import os
        os.remove(temp_audio_path)

        accuracy = 1.0 if expected_text.strip().lower() == transcribed_text.strip().lower() else 0.0
        feedback = "Good job!" if accuracy > 0.7 else "Try again, focus on pronunciation."

        return {
            "accuracy": accuracy,
            "feedback": feedback,
            "suggestions": [],
            "expected": expected_text,
            "heard": transcribed_text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pronunciation check failed: {str(e)}")


# ============================================================
# 🧮 Utility Endpoints
# ============================================================

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    vocab_categories = db.query(Vocabulary.category).distinct().all()
    lesson_categories = db.query(Lesson.category).distinct().all()
    all_categories = {cat[0] for cat in vocab_categories + lesson_categories}
    return {
        "categories": sorted(list(all_categories)),
        "vocabulary_categories": sorted([cat[0] for cat in vocab_categories]),
        "lesson_categories": sorted([cat[0] for cat in lesson_categories]),
    }


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_users": db.query(User).count(),
        "total_vocabulary": db.query(Vocabulary).count(),
        "total_lessons": db.query(Lesson).count(),
        "total_progress_entries": db.query(UserProgress).count(),
    }


# ============================================================
# 🚀 Run Server
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
