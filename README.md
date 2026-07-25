# AI-Powered Norwegian Language Learning App

A full-stack learning prototype that combines conversational AI, speech transcription, pronunciation feedback and teacher–student workflows. It was developed as a final Human-Centered AI project at Inland Norway University of Applied Sciences.

> This repository is currently private and is being retained as a portfolio project.

## User problem

Norwegian learners need more opportunities to practise conversation and pronunciation while still receiving structured guidance from a teacher. This application combines AI-assisted practice with human review rather than replacing the teacher.

## Main capabilities

### Student experience

- Build and browse Norwegian vocabulary
- Practise dialogue with an AI tutor
- Record or upload speech
- Receive transcription and pronunciation feedback
- Complete assigned pronunciation tasks
- Compare attempts and submit the best result

### Teacher experience

- Assign pronunciation tasks
- Review student submissions and accuracy
- Inspect transcribed speech
- Provide personalised written feedback

## Architecture

```text
Streamlit frontend
        ↓ REST API
FastAPI backend
   ├── GPT dialogue service
   ├── Whisper speech service
   └── SQLAlchemy / SQLite
```

## Technology

- Python
- FastAPI
- Streamlit
- OpenAI GPT and Whisper
- SQLAlchemy and SQLite
- Pydantic
- REST APIs
- Audio upload and microphone input

## Repository structure

```text
.
├── main.py
├── database.py
├── seed_data.py
├── ai/
│   ├── dialogue.py
│   └── speech.py
└── frontend/
    └── app.py
```

- `main.py`: API endpoints and service integration
- `database.py`: users, vocabulary, tasks and practice-attempt models
- `ai/dialogue.py`: adaptive Norwegian dialogue logic
- `ai/speech.py`: transcription and pronunciation analysis
- `frontend/app.py`: teacher and student interfaces

## Run locally

### 1. Create an environment

```bash
python -m venv .venv
```

Activate it and install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure the API key

Create a local `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

Never commit the real key.

### 3. Initialize and run

```bash
python seed_data.py
uvicorn main:app --reload
```

In a second terminal:

```bash
streamlit run frontend/app.py
```

## Human-centered design choices

- Separates student and teacher roles
- Keeps teachers involved in task assignment and final feedback
- Gives learners repeated practice opportunities
- Adapts dialogue to the learner's difficulty level
- Communicates when online AI services are unavailable

## Current limitations

- Local SQLite storage
- No production authentication or role-based authorization
- Requires network access and an OpenAI API key
- Pronunciation estimates depend on recording quality
- Temporary audio handling needs additional security hardening
- A production deployment would require tests, monitoring, privacy controls and consent mechanisms

## Possible next steps

- Secure authentication and role-based access
- PostgreSQL and cloud deployment
- Automated tests and CI
- Privacy and retention controls for voice recordings
- Learning-progress analytics
- Structured usability evaluation with students and teachers

## Context

Developed for Human-Centered Artificial Intelligence at Inland Norway University of Applied Sciences.

## Author

Rami — AI bachelor student with a professional background in chemistry, pharmaceutical quality control, technical training and regulated environments.
