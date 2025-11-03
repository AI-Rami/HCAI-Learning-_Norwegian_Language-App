from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy import Float
# Database setup
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'norwegian_learning.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
#  USER TABLE
# ------------------------------------------------------------
# Added to handle both students and teachers.
# Keeps simple text-based references to avoid breaking old logic.
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String, default="student")  # "student" or "teacher"
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
#  VOCABULARY TABLE
# ------------------------------------------------------------
# Unchanged from original file.
# ============================================================

class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    norwegian_word = Column(String, index=True)
    english_translation = Column(String)
    category = Column(String)
    difficulty_level = Column(Integer)
    pronunciation_guide = Column(String)
    example_sentence = Column(Text)


# ============================================================
#  TASK TABLE
# ------------------------------------------------------------
# Original version (kept identical)
# + Added optional link to TaskAttempt table for retry system.
# ============================================================

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    teacher = Column(String, nullable=False)
    student = Column(String, nullable=False)
    sentence = Column(String, nullable=False)
    accuracy = Column(Float, nullable=True)
    heard = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Added link to attempts
    attempts = relationship("TaskAttempt", back_populates="task", cascade="all, delete")

    def __repr__(self):
        return f"<Task(student='{self.student}', sentence='{self.sentence}', status='{self.status}')>"


# ============================================================
#  TASK ATTEMPTS (NEW)
# ------------------------------------------------------------
# Each Task can have multiple attempts by a student before submission.
# Keeps accuracy, heard text, and timestamp for each try.
# ============================================================

class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    accuracy = Column(Float, nullable=True)
    heard = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="attempts")

    def __repr__(self):
        return f"<TaskAttempt(task_id={self.task_id}, accuracy={self.accuracy})>"


# ============================================================
#  DATABASE INITIALIZATION
# ------------------------------------------------------------
# Creates all tables if not exist.
# ============================================================

def init_db():
    Base.metadata.create_all(bind=engine)


# ============================================================
#  SESSION DEPENDENCY
# ------------------------------------------------------------
# Used by FastAPI for database operations.
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
