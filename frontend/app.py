"""
app.py

Streamlit Frontend for the Norwegian Language Learning App

Overview:

This Streamlit application serves as the user interface for the Human-Centered AI
Norwegian Learning system. It connects to the FastAPI backend and provides
two separate interfaces:

1. Student Interface
   - Add and browse vocabulary
   - Practice AI-powered dialogue
   - Record and analyze pronunciation (speech practice)
   - View and submit assigned tasks with teacher feedback

2. Teacher Interface
   - Assign pronunciation tasks to students
   - Review student submissions
   - Send personalized feedback

The app uses the REST API endpoints provided by the FastAPI backend
(`http://localhost:8000` by default).
"""

# IMPORTS

# Streamlit builds the web UI
# Requests handles communication with the FastAPI backend
# datetime is used for time stamps on practice attempts
# The microphone feature (streamlit_mic_recorder)

import streamlit as st
import requests
from datetime import datetime

#  microphone recording
try:
    from streamlit_mic_recorder import mic_recorder
    _HAS_REC = True
except Exception:
    _HAS_REC = False



# API CONFIGURATION
# Local Deployment :
API_BASE = "http://localhost:8000"


# Online Deployment :
 # API_BASE = "https://norwegian-ai-backend.onrender.com"

# Page layout setup
st.set_page_config(page_title="Norwegian Learning App", page_icon="🇳🇴", layout="centered")


# HELPER FUNCTIONS

def _tone_style(tone: str):
    """
    Map a tone (string) to an emoji and color.

    """
    tone = (tone or "").lower()
    if tone == "praise":
        return "😊", "#4caf50"
    if tone == "encouraging":
        return "💪", "#ff9800"
    return "😐", "#2196f3"



# ROLE SELECTION (ONBOARDING)

# At startup, users choose their role: Student or Teacher.
# The selection determines which interface is loaded below.
# The role is stored in Streamlit's session state.


if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    st.title(" Welcome to the Norwegian Learning App")
    st.markdown("""
    Choose your role to continue:

    -  🎓Student: Learn Norwegian, practice speaking, and complete your tasks.
    -    Teacher: Assign and review pronunciation tasks.
    """)
    choice = st.radio("Select your role:", ["Student", "Teacher"])
    if st.button(" Continue"):
        st.session_state.role = choice
        st.rerun()
    st.stop()



# SIDEBAR CONFIGURATION

# Displays current backend connection info and a button to
# switch back to the role selection screen.


st.sidebar.caption(f" Connected to: {API_BASE}")
if st.sidebar.button(" Switch Role"):
    st.session_state.role = None
    st.rerun()



# TEACHER INTERFACE

# This interface provides two tabs:
#   1. Assign Task – send a new pronunciation sentence to a student
#   2. Review Students – view completed tasks, see accuracy, and send feedback


if st.session_state.role == "Teacher":
    st.title(" Teacher Dashboard")

    tabs = st.tabs([" Assign Task", " Review Students"])


    # TAB 1 — ASSIGN TASK

    with tabs[0]:
        st.subheader("Assign a new task")
        teacher_name = st.text_input("Teacher name:", "Teacher1")
        student_name = st.text_input("Student name:")
        sentence = st.text_area("Sentence to practice:")

        if st.button("📤 Send Task"):
            if student_name and sentence:
                data = {"teacher": teacher_name, "student": student_name, "sentence": sentence}
                res = requests.post(f"{API_BASE}/teacher/task", data=data)
                if res.status_code == 200:
                    st.success(" Task assigned successfully!")
                else:
                    st.error(f" Error: {res.text}")
            else:
                st.warning("Please fill in both fields before sending.")


    # TAB 2 — REVIEW STUDENTS

    with tabs[1]:
        st.subheader("Review submitted tasks")
        res = requests.get(f"{API_BASE}/teacher/review")

        if res.status_code == 200:
            tasks = res.json()
            if not tasks:
                st.info("No completed tasks yet.")

            # Show each student's completed sentence in collapsible panels
            for t in tasks:
                with st.expander(f"🎓 {t['student']} — {t['sentence']}"):
                    raw_acc = t.get("accuracy", None)
                    if raw_acc is not None:
                        st.markdown(f"Accuracy: {round(raw_acc * 100, 1)}%")
                    else:
                        st.markdown("Accuracy: -")
                    st.markdown(f"Heard: {t.get('heard', '-')}")  # student’s transcribed speech
                    st.markdown(f"Status: {t.get('status', '-')}")

                    # Feedback editor
                    feedback_text = st.text_area("Write feedback:", t.get('feedback', ''), key=f"f_{t['id']}")
                    if st.button(" Send Feedback", key=f"fb_{t['id']}"):
                        data = {"task_id": t["id"], "feedback": feedback_text}
                        r = requests.post(f"{API_BASE}/teacher/feedback", data=data)
                        if r.status_code == 200:
                            st.success("Feedback sent!")
                            st.rerun()
                        else:
                            st.error("Failed to send feedback.")
        else:
            st.error("Could not load tasks from server.")



# STUDENT INTERFACE

# Students can:
#   - Add vocabulary words
#   - Chat with AI in Norwegian
#   - Record and analyze pronunciation
#   - View and submit assigned tasks


elif st.session_state.role == "Student":
    st.title(" Student Page")

    # Require student name for task linking and data retrieval
    name = st.text_input("Your name:")
    if not name:
        st.stop()

    # Main navigation tabs
    tabs = st.tabs([" Vocabulary", " AI Dialogue", "️ Speech Practice", " My Tasks"])



    # TAB 1: VOCABULARY

    # Allows students to add new Norwegian–English word pairs and
    # browse all vocabulary items stored in the database.

    with tabs[0]:
        st.header(" Vocabulary")
        st.subheader("Add a new word")

        word = st.text_input("Norwegian word:")
        translation = st.text_input("English translation:")
        category = st.selectbox("Category", ["noun", "verb", "adjective", "greeting", "daily_life", "healthcare", "shopping", "other"])
        difficulty = st.slider("Difficulty", 1, 5, 1)
        example = st.text_area("Example sentence (optional):")

        # Add vocabulary entry
        if st.button("Add Word"):
            data = {
                "norwegian_word": word,
                "english_translation": translation,
                "category": category,
                "difficulty_level": difficulty,
                "example_sentence": example,
            }
            r = requests.post(f"{API_BASE}/vocabulary", json=data)
            if r.status_code == 201:
                st.success(" Added successfully!")
            else:
                st.error(" Error adding word.")

        # View existing vocabulary
        if st.button(" View Vocabulary List"):
            res = requests.get(f"{API_BASE}/vocabulary")
            if res.status_code == 200:
                vocab = res.json()
                for v in vocab:
                    with st.expander(f"{v['norwegian_word']} → {v['english_translation']}"):
                        st.write(f"Category: {v['category']}")
                        st.write(f"Example: {v.get('example_sentence', '-')}")
                        # Delete vocabulary button
                        if st.button(f"🗑 Delete '{v['norwegian_word']}'", key=f"del_{v['id']}"):
                            res_del = requests.delete(f"{API_BASE}/vocabulary/{v['id']}")
                            if res_del.status_code == 200:
                                st.success(" Word deleted successfully!")
                                st.rerun()
                            else:
                                st.error(" Failed to delete word.")

            else:
                st.error("Failed to load vocabulary.")



    # TAB 2: AI DIALOGUE

    # Chatbot practice using GPT-based dialogue tutor.
    # The user writes in English or Norwegian, and GPT replies in
    # Norwegian with translation and short tips based on difficulty level.

    with tabs[1]:
        st.header(" AI Dialogue Practice")

        # Keep chat history between reruns
        if "chat" not in st.session_state:
            st.session_state.chat = []

        # Display past messages
        for who, text in st.session_state.chat:
            st.markdown(f"**{who}:** {text}")

        # Compose new message
        msg = st.text_input("Write something (English or Norwegian):")
        diff = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"])

        # Send message to backend
        if st.button("Send"):
            if msg.strip():
                payload = {"message": msg, "difficulty_level": diff}
                r = requests.post(f"{API_BASE}/ai/dialogue", json=payload)
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.chat.append((" You", msg))
                    st.session_state.chat.append((" AI", f"{data['norwegian']}\n*{data['english']}*"))
                    st.rerun()

        # Clear conversation
        if st.button("🔄 Reset Chat"):
            st.session_state.chat = []
            st.success("Chat cleared.")
            st.rerun()



    # TAB 3: SPEECH PRACTICE

    # Three speech practice modes:
    #   1. Repeat a target sentence aloud
    #   2. Upload a pre-recorded audio file
    #   3. Speak freely for general pronunciation feedback

    with tabs[2]:
        st.header("️ Speech Practice")
        t1, t2, t3 = st.tabs(["🗣 Repeat after me", "📂 Upload", "💬 Speak freely"])


        # Repeat after me (mic input)

        with t1:
            st.markdown("Record your voice to practice pronunciation.")
            if _HAS_REC:
                audio = mic_recorder(start_prompt="🎙 Start", stop_prompt="🛑 Stop", use_container_width=True)
                sent = st.text_input("Sentence to practice:")
                if audio and st.button(" Analyze"):
                    files = {"audio": ("mic.wav", audio["bytes"], "audio/wav")}
                    data = {"expected_text": sent}
                    r = requests.post(f"{API_BASE}/ai/speech/pronunciation", files=files, data=data)
                    if r.status_code == 200:
                        out = r.json()
                        acc = out.get("accuracy", 0)
                        acc_display = round(acc * 100, 1) if acc <= 1 else round(acc, 1)
                        st.progress(acc_display / 100)
                        st.markdown(f"**Accuracy:** {acc_display}%")
                        st.info(out.get("feedback", ""))
                        st.caption(f"Expected: {out['expected']} | Heard: {out['heard']}")
            else:
                st.warning("Microphone not available.")


        # Upload mode (file input)

        with t2:
            st.markdown("Upload a recording to check pronunciation.")
            file = st.file_uploader("Upload WAV/MP3", type=["wav", "mp3"])
            text = st.text_input("Sentence you said:")
            if st.button("Analyze Upload"):
                if file and text:
                    files = {"audio": (file.name, file, file.type)}
                    data = {"expected_text": text}
                    r = requests.post(f"{API_BASE}/ai/speech/pronunciation", files=files, data=data)
                    if r.status_code == 200:
                        out = r.json()
                        acc = out.get("accuracy", 0)
                        acc_display = round(acc * 100, 1) if acc <= 1 else round(acc, 1)
                        st.progress(acc_display / 100)
                        st.markdown(f"Accuracy: {acc_display}%")
                        st.write(out.get("feedback", ""))
                        st.caption(f"Expected: {out['expected']} | Heard: {out['heard']}")
                else:
                    st.warning("Please upload audio and enter text.")


        # Free speech mode

        with t3:
            st.markdown("Speak freely — AI will give general feedback.")
            if _HAS_REC:
                audio = mic_recorder(start_prompt="🎙 Speak", stop_prompt="🛑 Stop", use_container_width=True)
                if audio and st.button("💬 Get Feedback"):
                    files = {"audio": ("free.wav", audio["bytes"], "audio/wav")}
                    r = requests.post(f"{API_BASE}/ai/speech/free_feedback", files=files)
                    if r.status_code == 200:
                        out = r.json()
                        st.success(out.get("feedback", ""))
                        st.caption(out.get("heard", ""))
            else:
                st.warning("Microphone not available.")



    # TAB 4: MY TASKS

    # Displays all pronunciation tasks assigned by a teacher.
    # Students can:
    #   - Record multiple practice attempts
    #   - View feedback from the AI on each attempt
    #   - Submit their best attempt for teacher review

    with tabs[3]:
        st.header("🗓 My Tasks")
        r = requests.get(f"{API_BASE}/student/tasks", params={"student": name})

        if r.status_code == 200:
            tasks = r.json()
            if not tasks:
                st.info("No tasks yet.")

            # Store practice attempts locally (temporary UI memory)
            if "practice_attempts" not in st.session_state:
                st.session_state.practice_attempts = {}

            for t in tasks:
                st.markdown(f"### Sentence: {t['sentence']}")
                st.markdown(f" Status: {t['status']}")

                task_key = f"task_{t['id']}"
                attempts = st.session_state.practice_attempts.get(task_key, [])

                # Pending task → student can still practice and submit
                if t["status"] == "pending":
                    st.subheader(" Practice before submitting")

                    if _HAS_REC:
                        audio = mic_recorder(
                            start_prompt="🎙 Record practice attempt",
                            stop_prompt="🛑 Stop",
                            key=f"practice_rec_{t['id']}",
                            use_container_width=True
                        )

                        # Save a local attempt (not submitted yet)
                        if audio and st.button(" Save Practice Attempt", key=f"save_attempt_{t['id']}"):
                            files = {"audio": ("task_practice.wav", audio["bytes"], "audio/wav")}
                            data = {"expected_text": t["sentence"]}
                            res_ai = requests.post(f"{API_BASE}/ai/speech/pronunciation", files=files, data=data)

                            if res_ai.status_code == 200:
                                result = res_ai.json()
                                raw_acc = float(result.get("accuracy", 0.0))
                                heard = result.get("heard", "")
                                attempts.append({
                                    "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
                                    "accuracy": raw_acc,
                                    "heard": heard,
                                })
                                st.session_state.practice_attempts[task_key] = attempts
                                st.success("Practice attempt saved!")
                            else:
                                st.error("AI analysis failed. Please try again.")
                    else:
                        st.warning("Microphone not available.")

                    # Display local practice attempts
                    if attempts:
                        st.subheader(" Your Attempts")
                        for att in attempts:
                            acc_percent = round(att["accuracy"] * 100, 1)
                            st.markdown(f"⏱ {att['timestamp']} — Accuracy: {acc_percent}%")
                            st.caption(f"Heard: {att['heard']}")

                        # Submit the best attempt to teacher
                        if st.button(" Submit Final Task", key=f"submit_final_{t['id']}"):
                            best_attempt = max(attempts, key=lambda a: a["accuracy"])
                            data2 = {
                                "task_id": t["id"],
                                "accuracy": best_attempt["accuracy"],
                                "heard": best_attempt["heard"],
                            }
                            res2 = requests.post(f"{API_BASE}/student/submit", data=data2)
                            if res2.status_code == 200:
                                st.success(" Task submitted with your best attempt!")
                                st.rerun()
                            else:
                                st.error("Failed to save result to database.")
                    else:
                        st.info("Record and save a few practice attempts before submitting.")

                # Completed task → show accuracy and teacher feedback
                else:
                    st.markdown(f"Accuracy: {round(t.get('accuracy', 0.0) * 100, 1)}%")
                    st.markdown(f"Heard: {t.get('heard', '-')}")
                    st.markdown(f"Teacher Feedback: {t.get('feedback', '-')}")
                    st.markdown("---")

        else:
            st.error("Failed to load tasks.")
