"""
main.py
--------
FastAPI backend for the Norwegian Language Learning App.

🧩 Purpose:
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
    """Analyze pronunciation against target text using Whisper + GPT."""
    global speech_ai, dialogue_ai

    # Save audio temporarily
    temp_audio_path = f"temp_{audio.filename}"
    with open(temp_audio_path, "wb") as f:
        f.write(await audio.read())

    # Step 1 — Transcribe with Whisper
    heard = speech_ai.transcribe_audio(temp_audio_path, language="no")
    os.remove(temp_audio_path)

    # Step 2 — Compare expected vs heard
    similarity = SequenceMatcher(None, expected_text.lower(), heard.lower()).ratio()

    # Step 3 — Ask GPT for friendly feedback
    prompt = f"""
    You are a kind Norwegian pronunciation coach.
    The learner tried to say: '{expected_text}'
    Whisper heard: '{heard}'
    Similarity: {similarity:.2f}

    Respond in JSON with:
    {{
      "accuracy": 0.85,
      "feedback": "Good pronunciation / God uttale",
      "emotion_tone": "praise",
      "semantic": "Clear and natural phrasing"
    }}
    """

    try:
        resp = dialogue_ai.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=250,
        )
        raw = resp.choices[0].message.content.strip().strip("`").replace("json", "")
        gpt_data = json.loads(raw)
    except Exception as e:
        gpt_data = {"accuracy": similarity, "feedback": f"(GPT error: {e})", "emotion_tone": "neutral", "semantic": ""}

    return {
        "accuracy": gpt_data.get("accuracy", similarity),
        "feedback": gpt_data.get("feedback", ""),
        "emotion_tone": gpt_data.get("emotion_tone", "neutral"),
        "semantic": gpt_data.get("semantic", ""),
        "expected": expected_text,
        "heard": heard,
    }


@app.post("/ai/speech/free_feedback")
async def free_feedback(audio: UploadFile = File(...)):
    """Freestyle mode — AI analyzes your natural speech."""
    global speech_ai, dialogue_ai

    temp_audio_path = f"temp_{audio.filename}"
    with open(temp_audio_path, "wb") as f:
        f.write(await audio.read())

    heard = speech_ai.transcribe_audio(temp_audio_path, language="no")
    os.remove(temp_audio_path)

    prompt = f"""
    You are a warm Norwegian teacher. The learner said: '{heard}'.
    Return JSON with pronunciation score, bilingual feedback, emotion tone, and semantic comment.
    """

    try:
        resp = dialogue_ai.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=250,
        )
        raw = resp.choices[0].message.content.strip().strip("`").replace("json", "")
        data = json.loads(raw)
    except Exception as e:
        data = {"accuracy": 0.0, "feedback": f"(GPT feedback unavailable: {e})", "emotion_tone": "neutral", "semantic": ""}

    return {"heard": heard, **data}


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
