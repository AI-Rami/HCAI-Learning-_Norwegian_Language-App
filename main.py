"""
FastAPI Backend for Norwegian Language Learning App
A Human-Centered AI application to help refugees learn basic Norwegian
"""
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import (
    init_db, get_db, User, Vocabulary, Lesson, UserProgress
)
from ai.dialogue import NorwegianDialogueAI
from ai.speech import WhisperSpeechToText

# Initialize FastAPI app
app = FastAPI(
    title="Norwegian Language Learning API",
    description="API for helping refugees learn Norwegian with AI assistance",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI modules
dialogue_ai = NorwegianDialogueAI()
speech_ai = WhisperSpeechToText(model_size="base")


# Pydantic models for request/response
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


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


# Root endpoint
@app.get("/")
def read_root():
    return {
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


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ==================== VOCABULARY ENDPOINTS ====================

@app.get("/vocabulary", response_model=List[VocabularyResponse])
def get_vocabulary(
    category: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get vocabulary words with optional filtering"""
    query = db.query(Vocabulary)
    
    if category:
        query = query.filter(Vocabulary.category == category)
    if difficulty_level:
        query = query.filter(Vocabulary.difficulty_level == difficulty_level)
    
    vocabulary = query.offset(skip).limit(limit).all()
    return vocabulary


@app.get("/vocabulary/{vocabulary_id}", response_model=VocabularyResponse)
def get_vocabulary_by_id(vocabulary_id: int, db: Session = Depends(get_db)):
    """Get a specific vocabulary word by ID"""
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    return vocab


@app.post("/vocabulary", response_model=VocabularyResponse, status_code=201)
def create_vocabulary(vocabulary: VocabularyCreate, db: Session = Depends(get_db)):
    """Create a new vocabulary word"""
    db_vocabulary = Vocabulary(**vocabulary.dict())
    db.add(db_vocabulary)
    db.commit()
    db.refresh(db_vocabulary)
    return db_vocabulary


# ==================== LESSON ENDPOINTS ====================

@app.get("/lessons", response_model=List[LessonResponse])
def get_lessons(
    category: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get lessons with optional filtering"""
    query = db.query(Lesson)
    
    if category:
        query = query.filter(Lesson.category == category)
    if difficulty_level:
        query = query.filter(Lesson.difficulty_level == difficulty_level)
    
    lessons = query.offset(skip).limit(limit).all()
    return lessons


@app.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson_by_id(lesson_id: int, db: Session = Depends(get_db)):
    """Get a specific lesson by ID"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@app.post("/lessons", response_model=LessonResponse, status_code=201)
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db)):
    """Create a new lesson"""
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


# ==================== USER ENDPOINTS ====================

@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==================== USER PROGRESS ENDPOINTS ====================

@app.get("/progress", response_model=List[ProgressResponse])
def get_all_progress(
    user_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get user progress with optional filtering"""
    query = db.query(UserProgress)
    
    if user_id:
        query = query.filter(UserProgress.user_id == user_id)
    if lesson_id:
        query = query.filter(UserProgress.lesson_id == lesson_id)
    
    progress = query.offset(skip).limit(limit).all()
    return progress


@app.get("/progress/{progress_id}", response_model=ProgressResponse)
def get_progress_by_id(progress_id: int, db: Session = Depends(get_db)):
    """Get specific progress entry by ID"""
    progress = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return progress


@app.post("/progress", response_model=ProgressResponse, status_code=201)
def create_progress(progress: ProgressCreate, db: Session = Depends(get_db)):
    """Create a new progress entry"""
    # Verify user and lesson exist
    user = db.query(User).filter(User.id == progress.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lesson = db.query(Lesson).filter(Lesson.id == progress.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    db_progress = UserProgress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


@app.put("/progress/{progress_id}", response_model=ProgressResponse)
def update_progress(
    progress_id: int,
    progress_update: ProgressUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing progress entry"""
    db_progress = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if not db_progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    
    # Update fields
    if progress_update.completed is not None:
        db_progress.completed = progress_update.completed
    if progress_update.score is not None:
        db_progress.score = progress_update.score
    
    db_progress.last_accessed = datetime.utcnow()
    
    db.commit()
    db.refresh(db_progress)
    return db_progress


# ==================== AI DIALOGUE ENDPOINTS ====================

@app.post("/ai/dialogue", response_model=DialogueResponse)
def practice_dialogue(request: DialogueRequest):
    """Practice Norwegian dialogue with AI"""
    response = dialogue_ai.generate_response(
        request.message,
        request.difficulty_level
    )
    
    return {
        "norwegian": response.get("norwegian", ""),
        "english": response.get("english", ""),
        "explanation": response.get("explanation", "")
    }


@app.post("/ai/dialogue/reset")
def reset_dialogue():
    """Reset dialogue conversation history"""
    dialogue_ai.reset_conversation()
    return {"message": "Conversation history reset"}


@app.get("/ai/dialogue/topic/{category}")
def get_practice_topic(category: str):
    """Get a practice dialogue topic by category"""
    topic = dialogue_ai.get_practice_topic(category)
    return topic


# ==================== AI SPEECH ENDPOINTS ====================

@app.post("/ai/speech/transcribe")
async def transcribe_speech(audio: UploadFile = File(...)):
    """
    Transcribe audio to text using Whisper.
    Upload an audio file (MP3, WAV, etc.) for transcription.
    """
    try:
        audio_bytes = await audio.read()
        result = speech_ai.transcribe_audio(audio_bytes, language="no")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/ai/speech/pronunciation", response_model=PronunciationFeedback)
async def check_pronunciation(
    expected_text: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    Check pronunciation by comparing expected text with audio transcription.
    Provides feedback and suggestions for improvement.
    """
    try:
        # Transcribe the audio
        audio_bytes = await audio.read()
        transcription_result = speech_ai.transcribe_audio(audio_bytes, language="no")
        transcribed_text = transcription_result.get("text", "")
        
        # Compare with expected text
        feedback = speech_ai.compare_pronunciation(expected_text, transcribed_text)
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pronunciation check failed: {str(e)}"
        )


@app.get("/ai/speech/tips/{word}")
def get_pronunciation_tips(word: str):
    """Get pronunciation tips for a specific Norwegian word"""
    tips = speech_ai.get_pronunciation_tips(word)
    return tips


# ==================== UTILITY ENDPOINTS ====================

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all available categories for vocabulary and lessons"""
    vocab_categories = db.query(Vocabulary.category).distinct().all()
    lesson_categories = db.query(Lesson.category).distinct().all()
    
    all_categories = set()
    all_categories.update([cat[0] for cat in vocab_categories])
    all_categories.update([cat[0] for cat in lesson_categories])
    
    return {
        "categories": sorted(list(all_categories)),
        "vocabulary_categories": sorted([cat[0] for cat in vocab_categories]),
        "lesson_categories": sorted([cat[0] for cat in lesson_categories])
    }


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_users = db.query(User).count()
    total_vocabulary = db.query(Vocabulary).count()
    total_lessons = db.query(Lesson).count()
    total_progress_entries = db.query(UserProgress).count()
    
    return {
        "total_users": total_users,
        "total_vocabulary": total_vocabulary,
        "total_lessons": total_lessons,
        "total_progress_entries": total_progress_entries
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
