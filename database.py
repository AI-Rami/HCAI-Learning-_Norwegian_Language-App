from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# ============================================================
#  DATABASE CONFIGURATION
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'norwegian_learning.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
#  USER TABLE (Teacher / Student)
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String, default="student")   # "student" or "teacher"
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress = relationship("UserProgress", back_populates="user", cascade="all, delete")
    tasks = relationship("Task", back_populates="student_obj", foreign_keys="Task.student_id")
    assigned_tasks = relationship("Task", back_populates="teacher_obj", foreign_keys="Task.teacher_id")


# ============================================================
#  VOCABULARY TABLE
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
#  TASK TABLE (Teacher → Student)
# ============================================================
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sentence = Column(Text, nullable=False)
    accuracy = Column(Float, nullable=True)
    heard = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher_obj = relationship("User", back_populates="assigned_tasks", foreign_keys=[teacher_id])
    student_obj = relationship("User", back_populates="tasks", foreign_keys=[student_id])
    attempts = relationship("TaskAttempt", back_populates="task", cascade="all, delete")


# ============================================================
#  TASK ATTEMPT TABLE (Retry system)
# ============================================================
class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    accuracy = Column(Float)
    heard = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="attempts")


# ============================================================
#  DB INIT + DEPENDENCY
# ============================================================
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
