"""
database.py
------------
SQLite database setup for the Norwegian Learning App.

 Purpose:
This file defines the database connection and structure used by the FastAPI backend.
It now focuses only on the *Vocabulary* feature

Structure:
  1. Imports and configuration
  2. Database engine + session setup
  3. ORM model: Vocabulary
  4. Initialization and session dependency for FastAPI
"""

# ============================================================
#  IMPORTS
# ------------------------------------------------------------
# - os: to handle file paths
# - sqlalchemy: ORM for working with database tables
# - datetime: for automatic timestamps
# ============================================================

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base


# ============================================================
#  DATABASE CONFIGURATION
# ------------------------------------------------------------
# SQLite is used here — a lightweight local database stored in a file.
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "norwegian_app.db")

# Full path connection string for SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Engine connects to the database file
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite + multithreading
)

# Session factory — creates isolated database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


# ============================================================
#  VOCABULARY TABLE
# ------------------------------------------------------------
# Stores all Norwegian words, their translations, categories,
# and example sentences for the learning app.
# ============================================================

class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    norwegian_word = Column(String, nullable=False)
    english_translation = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    pronunciation_guide = Column(String, nullable=True)
    example_sentence = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Vocabulary(word='{self.norwegian_word}', translation='{self.english_translation}')>"


# ============================================================
#  DATABASE INITIALIZATION & SESSION HANDLER
# ------------------------------------------------------------
# init_db(): creates tables if missing.
# get_db(): used by FastAPI endpoints to open/close DB sessions safely.
# ============================================================

def init_db():
    """Create the database tables if they don’t exist."""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at: {DB_PATH}")


def get_db():
    """Dependency that yields a database session for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
