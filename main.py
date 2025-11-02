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
from difflib import SequenceMatcher
import json
import os

# Import from local modules
from database import init_db, get_db, Vocabulary
from ai.dialogue import NorwegianDialogueAI
from ai.speech import WhisperSpeechToText

# Load environment variables
load_dotenv()


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
    """Fetch vocabulary items (optionally filtered by category or difficulty)."""
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

    # Save uploaded audio to a temporary file
    temp_audio_path = f"temp_{audio.filename}"
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # Run full speech analysis (transcription + GPT feedback)
        result = speech_ai.analyze_pronunciation(expected_text, temp_audio_path)

        # Align field names with frontend expectations
        return {
            "accuracy": result.get("accuracy", 0.0),
            "feedback": result.get("feedback", ""),
            "emotion_tone": "neutral",  # default (no tone classification yet)
            "semantic_comment": result.get("gpt_feedback", ""),
            "expected": result.get("expected", expected_text),
            "heard": result.get("heard", ""),
            "speed_comment": result.get("speed_comment", ""),
            "highlights_html": result.get("highlights_html", None),
        }

    except Exception as e:
        return {"error": f"Pronunciation analysis failed: {e}"}

    finally:
        # Ensure cleanup even if analysis fails
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)



@app.post("/ai/speech/free_feedback")
async def free_feedback(audio: UploadFile = File(...)):
    """
    Freestyle pronunciation and fluency feedback.
    The learner speaks naturally — Whisper transcribes, GPT comments.
    """
    global speech_ai

    temp_audio_path = f"temp_{audio.filename}"
    try:
        # Save uploaded recording
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # Step 1 — Transcribe using Whisper
        heard = speech_ai.transcribe_audio(temp_audio_path, language="no")

        # Step 2 — Ask GPT for feedback
        msg = (
            "You are a Norwegian language tutor giving short feedback on pronunciation and meaning.\n"
            f"Learner said:\n{heard}\n\n"
            "Respond in this exact format:\n"
            "Accuracy: (a number between 0 and 1)\n"
            "Norsk: (1 sentence praising or correcting pronunciation)\n"
            "English: (the same feedback translated)\n"
            "Semantic: (1 short comment on fluency or phrasing)\n\n"
            "Keep each section on its own line. Do not use lists or extra formatting."
        )

        resp = speech_ai.client.chat.completions.create(
            model="gpt-4o",
            temperature=0.5,
            max_tokens=300,
            messages=[
                {"role": "system", "content": "Be kind, encouraging, and concise."},
                {"role": "user", "content": msg},
            ],
        )

        gpt_text = resp.choices[0].message.content.strip()

        # Step 3 — Build response (no fragile JSON parsing)
        return {
            "heard": heard,
            "accuracy": 0.85,  # static placeholder (GPT doesn't compute numeric)
            "feedback": gpt_text,
            "emotion_tone": "encouraging",
            "semantic_comment": "",
        }

    except Exception as e:
        return {"error": f"Free feedback failed: {e}"}

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)



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