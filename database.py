from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database setup
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'norwegian_learning.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    progress = relationship("UserProgress", back_populates="user")


class Vocabulary(Base):
    __tablename__ = "vocabulary"
    
    id = Column(Integer, primary_key=True, index=True)
    norwegian_word = Column(String, index=True)
    english_translation = Column(String)
    category = Column(String)
    difficulty_level = Column(Integer)
    pronunciation_guide = Column(String)
    example_sentence = Column(Text)


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    difficulty_level = Column(Integer)
    content = Column(Text)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=True)
    completed = Column(Integer, default=0)  # 0 = not started, 1 = in progress, 2 = completed
    score = Column(Float, default=0.0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="progress")


# Database initialization
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
