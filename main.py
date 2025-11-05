"""
main.py
--------
Backend (FastAPI) for the Norwegian Language Learning App.

This file runs the API that connects to:
  - The SQLite database (users, vocabulary, tasks, etc.)
  - GPT (for AI dialogue)
  - Whisper (for speech analysis and pronunciation feedback)

It supports both students and teachers.
Students can learn words, practice pronunciation, and chat with AI.
Teachers can assign tasks, check results, and give feedback.
"""


# IMPORTS

# FastAPI: framework that runs the backend API.
# SQLAlchemy: connects and saves data to the database.
# Pydantic: checks incoming and outgoing data formats.
# dotenv: loads environment variables like the OpenAI key.
# datetime: helps store timestamps.
# ============================================================

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os

# Local project files
from database import init_db, get_db, User, Vocabulary, Task, TaskAttempt
from ai.dialogue import NorwegianDialogueAI
from ai.speech import WhisperSpeechToText

# Load OpenAI key and any other environment variables from .env
load_dotenv()


# APP SETUP

# Creates the FastAPI application.
# CORS middleware allows the frontend (Streamlit) to connect.
# ============================================================

app = FastAPI(
    title="Norwegian Learning API",
    description="Backend for the Norwegian Language Learning App with AI dialogue, speech feedback, and teacher–student system.",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load AI models (GPT and Whisper) when the app starts
dialogue_ai = None
speech_ai = None

@app.on_event("startup")
def startup_event():
    """Runs automatically when the API starts."""
    global dialogue_ai, speech_ai
    init_db()  # Create tables if they don’t exist
    dialogue_ai = NorwegianDialogueAI()  # GPT for AI dialogue
    speech_ai = WhisperSpeechToText()    # Whisper for pronunciation



# USER ENDPOINTS

# Manage students and teachers in the database.


class UserCreate(BaseModel):
    username: str
    role: str = "student"
    email: Optional[str] = None


@app.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Add a new user (student or teacher)."""
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
    """List all users. Can filter by role (student/teacher)."""
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    return q.order_by(User.created_at.desc()).all()


#
# DATA MODELS FOR REQUESTS AND RESPONSES

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



# ROOT AND HEALTH ENDPOINTS

# Used to test that the API is online.


@app.get("/")
def read_root():
    """Main page for the API. Shows available routes."""
    return {
        "message": "Welcome to the Norwegian Learning API",
        "version": "2.2.0",
        "available_endpoints": [
            "/vocabulary", "/ai/dialogue", "/ai/speech/pronunciation", "/ai/speech/free_feedback"
        ],
    }


@app.get("/health")
def health_check():
    """Used for checking if the backend is running."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}



# VOCABULARY ENDPOINTS

# Let the app store and read vocabulary words.
# Students can add new words and view existing ones.


@app.get("/vocabulary", response_model=List[VocabularyResponse])
def get_vocabulary(
    category: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all vocabulary words """
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
    """Delete a vocabulary word by its ID."""
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocabulary_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    db.delete(vocab)
    db.commit()
    return {"message": f"✅ Word {vocabulary_id} deleted successfully"}



# AI DIALOGUE ENDPOINTS

# Handles chat between the user and GPT-based Norwegian tutor.
# The AI adapts to the user's difficulty level.


@app.post("/ai/dialogue", response_model=DialogueResponse)
def practice_dialogue(request: DialogueRequest):
    """Generate AI reply (in Norwegian + English)."""
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
    """Clear previous chat memory."""
    global dialogue_ai
    dialogue_ai.reset()
    return {"message": "🧹 Chat history cleared."}


# ============================================================
# SPEECH ENDPOINTS (Whisper + GPT)
# ============================================================
# 1. /ai/speech/pronunciation → compares student’s pronunciation with target sentence
# 2. /ai/speech/free_feedback → general feedback on free speech
# ============================================================

@app.post("/ai/speech/pronunciation")
async def check_pronunciation(
    expected_text: str = Form(...),
    audio: UploadFile = File(...),
):
    """Check pronunciation and return accuracy + GPT feedback."""
    global speech_ai
    temp_audio_path = f"temp_{audio.filename}"
    try:
        # Save temporary file and send it to Whisper + GPT
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
    """Give general pronunciation and fluency feedback (no score)."""
    global speech_ai
    temp_audio_path = f"temp_{audio.filename}"

    try:
        # Save temporary recording
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # Step 1: Transcribe what the student said
        heard = speech_ai.transcribe_audio(temp_audio_path, language="no")

        # Step 2: Ask GPT for feedback
        msg = (
            "You are an experienced Norwegian language tutor and pronunciation coach. "
            "The learner just spoke freely in Norwegian — give short, friendly feedback "
            "about pronunciation, grammar, and how natural it sounds."
        )

        resp = speech_ai.client.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            max_tokens=350,
            messages=[
                {"role": "system", "content": "Be warm and natural like a real Norwegian teacher."},
                {"role": "user", "content": msg + f"\n\n🎧 Speech:\n{heard}"},
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
# TEACHER–STUDENT ENDPOINTS
# ============================================================
# Teachers can assign tasks.
# Students can see, practice, submit, and get feedback.
# ============================================================

@app.post("/teacher/task")
def assign_task(
    teacher: str = Form(...),
    student: str = Form(...),
    sentence: str = Form(...),
    db: Session = Depends(get_db)
):
    """Teacher creates a new pronunciation task for a student."""
    task = Task(teacher=teacher, student=student, sentence=sentence)
    db.add(task)
    db.commit()
    return {"message": "Task assigned successfully."}


@app.get("/student/tasks")
def get_student_tasks(student: str, db: Session = Depends(get_db)):
    """List all tasks assigned to a specific student."""
    return db.query(Task).filter(Task.student == student).order_by(Task.created_at.desc()).all()


@app.post("/student/submit")
def submit_task(
    task_id: int = Form(...),
    accuracy: float = Form(...),
    heard: str = Form(...),
    db: Session = Depends(get_db)
):
    """Student submits their best pronunciation result."""
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
    """Teacher adds written feedback to a completed task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.feedback = feedback
    db.commit()
    return {"message": "Feedback saved."}


@app.get("/teacher/review")
def review_tasks(db: Session = Depends(get_db)):
    """Show all student tasks (for teacher review)."""
    return db.query(Task).order_by(Task.created_at.desc()).all()


# ============================================================
# TASK ATTEMPTS (RETRY SYSTEM)
# ============================================================
# Students can record several practice attempts before submitting.
# Each attempt is stored separately.
# ============================================================

@app.post("/student/retry")
async def record_attempt(
    task_id: int = Form(...),
    expected_text: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Save a student's extra practice attempt (not final submission)."""
    global speech_ai
    temp_audio_path = f"temp_{audio.filename}"
    try:
        # Save temporary file
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # Analyze pronunciation using Whisper + GPT
        result = speech_ai.analyze_pronunciation(expected_text, temp_audio_path)

        # Save result as a new attempt record
        attempt = TaskAttempt(
            task_id=task_id,
            accuracy=result.get("accuracy", 0.0),
            heard=result.get("heard", "")
        )
        db.add(attempt)
        db.commit()

        # Return AI feedback (task status not changed yet)
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
    """List all recorded attempts for one specific task."""
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
# RUN THE SERVER (LOCAL USE)
# ============================================================
# Use this only for testing locally:
#     python main.py
# For deployment, use:
#     uvicorn main:app
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
