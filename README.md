===========================================================
Norwegian Language Learning App (Final HCAI Exam Project)
===========================================================

Author: Rami Badleh  
Course: Human-Centered Artificial Intelligence (KIUA1008)  
Institution: Inland Norway University of Applied Sciences  
Year: 2025  
===========================================================


1. Project Overview
-------------------
This project is an AI-powered language learning system designed
to help learners practice Norwegian in an interactive way.

The app provides two main interfaces:

• Student interface:
  - Learn new Norwegian words (Vocabulary)
  - Chat with an AI language tutor (GPT)
  - Record and analyze speech pronunciation (Whisper)
  - Receive tasks from teachers and submit attempts

• Teacher interface:
  - Assign pronunciation tasks
  - Review student submissions
  - Send written feedback directly from the dashboard


2. System Components
--------------------
The project has two main parts:

1) Backend (FastAPI) — main.py
   - Handles API requests and connects everything together.
   - Uses GPT (for dialogue), Whisper (for speech), and SQLite (for storage).

2) Frontend (Streamlit) — app.py
   - Web interface for both teacher and student users.
   - Connects to FastAPI backend via REST API calls.

Supporting files:
   - database.py  → defines all database tables.
   - dialogue.py  → controls AI dialogue and correction logic.
   - speech.py    → manages audio transcription and feedback.
   - seed_data.py → fills the database with initial sample words.


3. Features Summary
-------------------
STUDENT FUNCTIONS:
- Add, view, and categorize vocabulary.
- Chat with GPT to practice Norwegian (with correction + translation).
- Record speech and receive pronunciation accuracy and feedback.
- Review assigned pronunciation tasks and submit best attempt.

TEACHER FUNCTIONS:
- Assign new speaking tasks.
- Review student performance and accuracy.
- Provide personalized written feedback.


4. Technology Stack
-------------------
Languages:
  - Python 3.10+

Frameworks and Libraries:
  - FastAPI (backend API)
  - Streamlit (frontend UI)
  - SQLAlchemy (database ORM)
  - OpenAI (GPT and Whisper)
  - Pydantic (data validation)
  - Requests (API communication)
  - pydub (optional audio processing)
  - streamlit-mic-recorder (optional microphone recording)

Database:
  - SQLite (local file-based database)


5. Installation & Setup
-----------------------
Follow these steps to set up and run the app locally.

Step 1: Create a virtual environment
------------------------------------
  python -m venv .venv
  source .venv/bin/activate   (Mac/Linux)
  .venv\Scripts\activate      (Windows)

Step 2: Install dependencies
----------------------------
  pip install -r requirements.txt

Step 3: Add your OpenAI API key
-------------------------------
Create a file named `.env` in the project folder and add:
  OPENAI_API_KEY=your_api_key_here

Step 4: Initialize the database
-------------------------------
  python seed_data.py

Step 5: Run the backend server
------------------------------
  uvicorn main:app --reload

Step 6: Run the frontend (Streamlit)
------------------------------------
  streamlit run app.py


6. Folder Structure
-------------------
/project-folder
│
├── app.py                → Streamlit interface (teacher/student)
├── main.py               → FastAPI backend
├── database.py           → Database models (User, Vocabulary, Task)
├── dialogue.py           → GPT-based Norwegian tutor logic
├── speech.py             → Whisper + GPT pronunciation feedback
├── seed_data.py          → Adds initial vocabulary examples
├── requirements.txt      → List of dependencies
├── .env                  → (Your API key)
└── norwegian_learning.db → SQLite database file (created automatically)


7. Example Usage
----------------
After running both backend and frontend:

- Open Streamlit in your browser.
- Choose your role:
    👨‍🎓 Student → Learn, chat, and practice.
    👩‍🏫 Teacher → Assign and review tasks.
- Students can speak or upload audio.
- Teachers can monitor performance in real-time.


8. Notes & Limitations
----------------------
- This version uses OpenAI’s GPT and Whisper models online.
  (Requires internet and valid API key.)
- Speech analysis may vary based on microphone quality.
- Database is local — all data is saved to norwegian_learning.db.


9. Credits
-----------
Developed by: Rami Badleh  
Under supervision of: Inland Norway University of Applied Sciences  
For the course: Human-Centered Artificial Intelligence (KIUA1008)

Technologies: OpenAI GPT-4o, Whisper, FastAPI, Streamlit, SQLite


===========================================================
End of README
===========================================================
