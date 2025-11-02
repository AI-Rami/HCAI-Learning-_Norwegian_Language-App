Norwegian Language Learning App
--------------------------------

A Human-Centered AI web application built to help users practice Norwegian
vocabulary, conversation, and pronunciation — powered by FastAPI, Streamlit,
and OpenAI models.


CORE FEATURES
-------------
• Vocabulary Management
  Add, edit, delete, and browse Norwegian words with translations and examples.

• AI Dialogue Practice
  Chat naturally in Norwegian with an AI tutor that adapts to your difficulty level
  (beginner, intermediate, advanced).

• Pronunciation Feedback
  Record or upload your speech and get instant pronunciation feedback using
  Whisper + GPT.


PROJECT STRUCTURE
-----------------
HCAI-Learning-Norwegian-Language-App/
├── main.py              → FastAPI backend (vocabulary + AI)
├── database.py          → SQLite database (vocabulary table)
├── ai/
│   ├── __init__.py      → AI package marker
│   ├── dialogue.py      → GPT-based dialogue tutor
│   └── speech.py        → Whisper speech-to-text & feedback
├── seed_data.py         → Seeds vocabulary data
├── app.py               → Streamlit frontend
├── requirements.txt     → Dependencies
└── README.txt           → This file


INSTALLATION
------------
1. Make sure you have Python 3.13 or higher.
2. Clone or download the project.
3. Open a terminal inside the project folder and run:

   python -m venv venv
   venv\Scripts\activate        (on macOS/Linux: source venv/bin/activate)
   pip install -r requirements.txt


INITIALIZE DATABASE
-------------------
python seed_data.py


RUN THE BACKEND (FASTAPI)
-------------------------
uvicorn main:app --reload
API available at: http://localhost:8000


RUN THE FRONTEND (STREAMLIT)
----------------------------
streamlit run app.py


API OVERVIEW
------------
/vocabulary                → GET  - list all words (filter optional)
/vocabulary                → POST - add new word
/vocabulary/{id}           → PUT  - update word
/vocabulary/{id}           → DELETE - delete word
/ai/dialogue               → POST - chat with AI tutor
/ai/dialogue/reset         → POST - clear chat
/ai/speech/pronunciation   → POST - pronunciation check
/ai/speech/free_feedback   → POST - free speaking feedback


DATABASE STRUCTURE
------------------
Table: vocabulary
Fields:
  id
  norwegian_word
  english_translation
  category
  difficulty_level
  pronunciation_guide
  example_sentence
  created_at


CONFIGURATION
-------------
Create a file called .env in the project folder and add:
OPENAI_API_KEY=your_api_key_here


TECH STACK
-----------
• FastAPI  — backend API
• Streamlit — web UI
• SQLite + SQLAlchemy — database
• OpenAI GPT + Whisper — AI tutor and speech analysis


ACKNOWLEDGMENT
--------------
Built for the Human-Centered AI Exam Project (KIUA1008)
Inland Norway University of Applied Sciences
