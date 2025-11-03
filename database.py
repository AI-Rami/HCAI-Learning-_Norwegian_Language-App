"""
database.py
------------
Database structure for the Norwegian Language Learning App
===========================================================

Purpose:
--------
This file defines the database used by both the backend (FastAPI)
and the frontend (Streamlit). It stores all main data about users,
vocabulary, tasks, and practice attempts.

Database type:
--------------
SQLite (lightweight local database stored in a .db file).

Main tables:
-------------
1. User          → basic info for students and teachers
2. Vocabulary    → Norwegian–English word pairs with examples
3. Task          → teacher-assigned pronunciation exercises
4. TaskAttempt   → student’s practice tries before submitting
"""

# ============================================================
# IMPORTS
# ============================================================
# SQLAlchemy: used to define tables and handle database actions
# datetime: automatically records creation times
# os: builds the database file path
# ============================================================

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# ============================================================
# DATABASE CONNECTION
# ============================================================
# Creates a local SQLite database file inside the project folder.
# (For example: /project-folder/norwegian_learning.db)
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'norwegian_learning.db')}"

# Connect and create tables when needed
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# TABLE: User
# ============================================================
# Stores information about both students and teachers.
# Each user has a name, role type, and optional email.
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String, default="student")  # Either "student" or "teacher"
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# TABLE: Vocabulary
# ============================================================
# Contains Norwegian words and their English translations.
# Includes example sentences and a difficulty level.
# This is the learning content students can browse or add to.
# ============================================================

class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    norwegian_word = Column(String, index=True)
    english_translation = Column(String)
    category = Column(String)               # e.g., “verb”, “noun”, “greeting”
    difficulty_level = Column(Integer)      # Scale from 1 (easy) to 5 (hard)
    pronunciation_guide = Column(String)    # Optional helper text
    example_sentence = Column(Text)         # Example of how to use the word


# ============================================================
# TABLE: Task
# ============================================================
# Represents a pronunciation assignment created by a teacher.
# Each task includes:
#   - teacher name
#   - student name
#   - sentence to practice
#   - accuracy and feedback fields (after submission)
# Linked to TaskAttempt to store student’s multiple practice tries.
# ============================================================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    teacher = Column(String, nullable=False)
    student = Column(String, nullable=False)
    sentence = Column(String, nullable=False)
    accuracy = Column(Float, nullable=True)     # 0–1 (final score)
    heard = Column(String, nullable=True)       # Transcribed student audio
    feedback = Column(String, nullable=True)    # Teacher feedback message
    status = Column(String, default="pending")  # “pending” or “done”
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-many: a task can have several attempts before final submission
    attempts = relationship("TaskAttempt", back_populates="task", cascade="all, delete")

    def __repr__(self):
        return f"<Task(student='{self.student}', sentence='{self.sentence}', status='{self.status}')>"


# ============================================================
# TABLE: TaskAttempt
# ============================================================
# Keeps track of every practice attempt a student makes before submitting.
# Stores:
#   - accuracy score
#   - what the model heard
#   - timestamp
# Linked to its parent Task.
# ============================================================

class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    accuracy = Column(Float, nullable=True)
    heard = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Each attempt belongs to one parent Task
    task = relationship("Task", back_populates="attempts")

    def __repr__(self):
        return f"<TaskAttempt(task_id={self.task_id}, accuracy={self.accuracy})>"


# ============================================================
# DATABASE INITIALIZATION
# ============================================================
# Creates all tables if they don’t exist yet.
# Called automatically when FastAPI starts.
# ============================================================

def init_db():
    Base.metadata.create_all(bind=engine)


# ============================================================
# SESSION MANAGEMENT
# ============================================================
# Provides a session object for reading/writing database data.
# Used inside FastAPI endpoints with “Depends(get_db)”.
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
