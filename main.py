"""
main.py
--------
FastAPI backend for the Norwegian Language Learning App.

 Purpose:
This backend connects Streamlit frontend to:
  • the vocabulary database (add, read, update, delete)
  • GPT-powered Norwegian dialogue tutor
  • Whisper + GPT pronunciation feedback



Structure:
  1. Imports and setup
  2. Pydantic models for validation
  3. FastAPI app initialization
  4. Vocabulary CRUD endpoints
  5. AI dialogue (GPT tutor)
  6. Speech pronunciation & free-talk feedback (Whisper + GPT)
"""

# ============================================================
#  IMPORTS
# ------------------------------------------------------------
# FastAPI — the web framework for serving API endpoints.
# SQLAlchemy — connects to the SQLite database through Session.
# Pydantic — validates request/response models.
# dotenv — loads environment variables (like the OpenAI API key).
# difflib — used for computing pronunciation similarity.
# ============================================================

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os

# Local modules
from database import init_db, get_db, User, Vocabulary, Task, TaskAttempt
from ai.dialogue import NorwegianDialogueAI
from ai.speech import WhisperSpeechToText

# Load environment variables
load_dotenv()

# ============================================================
#  FASTAPI APP SETUP
# ============================================================
app = FastAPI(
    title="Norwegian Learning API",
    description="Backend for the Norwegian Learning App with AI dialogue, speech feedback, and teacher–student system.",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dialogue_ai = None
speech_ai = None

@app.on_event("startup")
def startup_event():
    global dialogue_ai, speech_ai
    init_db()
    dialogue_ai = NorwegianDialogueAI()
    speech_ai = WhisperSpeechToText()



# ============================================================
#  USER ENDPOINTS
# ============================================================
class UserCreate(BaseModel):
    username: str
    role: str = "student"
    email: Optional[str] = None

@app.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user (teacher or student)."""
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User '{new_user.username}' created as {new_user.role}."}

@app.get("/users")
def list_users(role: Optional[str] = None, db: Session = Depends(get_db)):
    """List all users or filter by role."""
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    return q.order_by(User.created_at.desc()).all()




# ============================================================
# PYDANTIC MODELS
# ------------------------------------------------------------
# These define the expected structure for incoming and outgoing data.
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


class DialogueRequest(BaseModel):
    message: str
    difficulty_level: str = "beginner"


class DialogueResponse(BaseModel):
    norwegian: str
    english: str
    explanation: str


# ============================================================
# ️ FASTAPI APP SETUP
# ------------------------------------------------------------
# Creates the app instance and allows  frontend to communicate with it.
# ============================================================

app = FastAPI(
    title="Norwegian Learning API",
    description="Simplified backend combining GPT and Whisper for Norwegian learning.",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#  STARTUP EVENT
# ------------------------------------------------------------
# Initializes the database and AI models once when the server starts.
# ============================================================

dialogue_ai = None
speech_ai = None

@app.on_event("startup")
def startup_event():
    global dialogue_ai, speech_ai
    init_db()
    dialogue_ai = NorwegianDialogueAI()   # GPT-based dialogue model
    speech_ai = WhisperSpeechToText()     # Whisper-based transcription model


# ============================================================
# ROOT & HEALTH CHECK
# ------------------------------------------------------------
# Root: gives info and available routes.
# Health: used for simple uptime verification.
# ============================================================

@app.get("/")
def read_root():
    """Landing endpoint for info."""
    return {
        "message": "Welcome to the Norwegian Learning API",
        "version": "2.1.0",
        "available_endpoints": [
            "/vocabulary", "/ai/dialogue", "/ai/speech/pronunciation", "/ai/speech/free_feedback"
        ],
    }

@app.get("/health")
def health_check():
    """Quick deployment health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ============================================================
#  VOCABULARY ENDPOINTS (CRUD)
# ------------------------------------------------------------
# These endpoints let the frontend add, read, edit, and delete words.
# They directly read/write from the SQLite database.
# ============================================================

@app.get("/vocabulary", response_model=List[VocabularyResponse])
def get_vocabulary(
    category: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Fetch vocabulary items (optionally filtered)."""
    query = db.query(Vocabulary)
    if category:
        query = query.filter(Vocabulary.category == category)
    if difficulty_level:
        query = query.filter(Vocabulary.difficulty_level == difficulty_level)
    return query.offset(skip).limit(limit).all()


@app.post("/vocabulary", response_model=VocabularyResponse, status_code=201)
def create_vocabulary(vocabulary: VocabularyCreate, db: Session = Depends(get_db)):
    """Add a new Norwegian–English word pair."""
    db_vocabulary = Vocabulary(**vocabulary.dict())
    db.add(db_vocabulary)
    db.commit()
    db.refresh(db_vocabulary)
    return db_vocabulary


@app.put("/vocabulary/{vocabulary_id}", response_model=VocabularyResponse)
def update_vocabulary(vocabulary_id: int, updated_data: dict = Body(...), db: Session = Depends(get_db)):
    """Edit an existing vocabulary entry."""
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
    """Remove a word from the vocabulary list."""
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    db.delete(vocab)
    db.commit()
    return {"message": f"✅ Word {vocabulary_id} deleted successfully"}



# ============================================================
#  AI DIALOGUE ENDPOINTS
# ------------------------------------------------------------
# Handles chat-based conversation with GPT, acting as a tutor.
# Difficulty affects how complex the Norwegian reply will be.
# ============================================================

@app.post("/ai/dialogue", response_model=DialogueResponse)
def practice_dialogue(request: DialogueRequest):
    """Generate AI tutor reply in Norwegian + English translation."""
    global dialogue_ai
    reply = dialogue_ai.generate_response(request.message, request.difficulty_level)

    if "\n" in reply:
        norwegian, english = reply.split("\n", 1)
    else:
        norwegian, english = reply, ""
    return {
        "norwegian": norwegian.strip(),
        "english": english.strip(),
        "explanation": "AI-generated Norwegian tutor response."
    }


@app.post("/ai/dialogue/reset")
def reset_dialogue():
    """Clear chat memory to start a new conversation."""
    global dialogue_ai
    dialogue_ai.reset()
    return {"message": "🧹 Chat history cleared."}


# ============================================================
#  SPEECH ANALYSIS ENDPOINTS (Whisper + GPT)
# ------------------------------------------------------------
# 1️ check_pronunciation , user reads a target sentence
# 2️ free_feedback ,  user speaks freely
#
# Both use Whisper to transcribe audio and GPT to rate and comment.
# ============================================================

@app.post("/ai/speech/pronunciation")
async def check_pronunciation(
    expected_text: str = Form(...),
    audio: UploadFile = File(...),
):
    """
    Analyze pronunciation accuracy and give GPT feedback.
    Uses WhisperSpeechToText.analyze_pronunciation() for full pipeline.
    """
    global speech_ai
    temp_audio_path = f"temp_{audio.filename}"
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        result = speech_ai.analyze_pronunciation(expected_text, temp_audio_path)

        return {
            "accuracy": result.get("accuracy", 0.0),
            "feedback": result.get("feedback", ""),
            "expected": result.get("expected", expected_text),
            "heard": result.get("heard", ""),
            "speed_comment": result.get("speed_comment", ""),
            "highlights_html": result.get("highlights_html", None),
            "gpt_feedback": result.get("gpt_feedback", ""),
        }

    except Exception as e:
        return {"error": f"Pronunciation analysis failed: {e}"}

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


@app.post("/ai/speech/free_feedback")
async def free_feedback(audio: UploadFile = File(...)):
    """
    Freestyle pronunciation and fluency feedback (no accuracy scoring).
    The learner speaks freely — Whisper transcribes and GPT comments on pronunciation, grammar, and meaning.
    """
    global speech_ai
    temp_audio_path = f"temp_{audio.filename}"

    try:
        # Save the recording
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # Step 1 — Transcribe using Whisper
        heard = speech_ai.transcribe_audio(temp_audio_path, language="no")

        # Step 2 — Ask GPT for natural feedback
        msg = (
            "You are an experienced Norwegian language tutor and pronunciation coach. "
            "The learner just spoke freely in Norwegian — your job is to give holistic feedback. "
            "Evaluate the speech in three areas:\n"
            "1️⃣ Pronunciation – clarity, rhythm, vowel/consonant accuracy, stress.\n"
            "2️⃣ Grammar – sentence structure, word order, verb forms.\n"
            "3️⃣ Meaning – does it make sense, and how natural does it sound?\n\n"
            f"🎧 Transcribed speech:\n{heard}\n\n"
            "Then reply with this structure:\n"
            "🗣️ **Norwegian feedback:** 2–3 sentences in Norwegian giving praise and gentle correction.\n"
            "_Then provide the English translation below in italics._\n"
            "💡 **Tip (English):** Offer one short, practical improvement idea."
        )

        resp = speech_ai.client.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            max_tokens=350,
            messages=[
                {"role": "system", "content": "Be warm, supportive, and natural like a real Norwegian teacher."},
                {"role": "user", "content": msg},
            ],
        )

        feedback = resp.choices[0].message.content.strip()

        return {
            "heard": heard,
            "feedback": feedback,
            "emotion_tone": "supportive",
        }

    except Exception as e:
        return {"error": f"Free feedback failed: {e}"}

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)



# ============================================================
#  TEACHER–STUDENT COLLABORATION ENDPOINTS
# ------------------------------------------------------------
@app.post("/teacher/task")
def assign_task(
    teacher: str = Form(...),
    student: str = Form(...),
    sentence: str = Form(...),
    db: Session = Depends(get_db)
):
    """Teacher assigns a new sentence for a student to practice."""
    task = Task(teacher=teacher, student=student, sentence=sentence)
    db.add(task)
    db.commit()
    return {"message": "Task assigned successfully."}


@app.get("/student/tasks")
def get_student_tasks(student: str, db: Session = Depends(get_db)):
    """Return all tasks assigned to a given student."""
    return db.query(Task).filter(Task.student == student).order_by(Task.created_at.desc()).all()


@app.post("/student/submit")
def submit_task(
    task_id: int = Form(...),
    accuracy: float = Form(...),
    heard: str = Form(...),
    db: Session = Depends(get_db)
):
    """Student submits pronunciation accuracy and transcription."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.accuracy = accuracy
    task.heard = heard
    task.status = "done"
    db.commit()
    return {"message": "Result submitted successfully."}


@app.post("/teacher/feedback")
def teacher_feedback(
    task_id: int = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db)
):
    """Teacher sends written feedback after reviewing a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.feedback = feedback
    db.commit()
    return {"message": "Feedback saved."}


@app.get("/teacher/review")
def review_tasks(db: Session = Depends(get_db)):
    """Return all student tasks (most recent first)."""
    return db.query(Task).order_by(Task.created_at.desc()).all()



# ============================================================
#  TASK ATTEMPT ENDPOINTS (Retry System)
# ------------------------------------------------------------
# Allow students to record multiple attempts before submission.
# Each attempt is saved separately, linked to its parent task.
# ============================================================



@app.post("/student/retry")
async def record_attempt(
    task_id: int = Form(...),
    expected_text: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Save a student's new practice attempt for a given task.
    Does not mark task as submitted; used only for trying again.
    """
    global speech_ai
    temp_audio_path = f"temp_{audio.filename}"
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # Run pronunciation analysis
        result = speech_ai.analyze_pronunciation(expected_text, temp_audio_path)

        # Create a TaskAttempt entry
        attempt = TaskAttempt(
            task_id=task_id,
            accuracy=result.get("accuracy", 0.0),
            heard=result.get("heard", "")
        )
        db.add(attempt)
        db.commit()

        # Return feedback without changing task status
        return {
            "message": "Attempt recorded successfully.",
            "accuracy": result.get("accuracy", 0.0),
            "heard": result.get("heard", ""),
            "feedback": result.get("feedback", ""),
            "gpt_feedback": result.get("gpt_feedback", "")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attempt recording failed: {e}")

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


@app.get("/student/attempts/{task_id}")
def get_attempts(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all retry attempts for a specific task.
    Helps the student see progress before final submission.
    """
    attempts = db.query(TaskAttempt).filter(TaskAttempt.task_id == task_id).order_by(TaskAttempt.created_at.desc()).all()
    if not attempts:
        return {"message": "No attempts yet for this task."}
    return [
        {
            "id": a.id,
            "accuracy": a.accuracy,
            "heard": a.heard,
            "created_at": a.created_at.isoformat()
        }
        for a in attempts
    ]

# ============================================================
#  RUN SERVER (LOCAL DEVELOPMENT)
# ------------------------------------------------------------
# Launches Uvicorn server when run directly:
#     python main.py
# In deployment (Render, etc.), use: uvicorn main:app
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)