"""
app.py
-------
Streamlit frontend for the Norwegian Language Learning App.

 Purpose:
This app connects to  FastAPI backend and provides an intuitive interface
for learners to practice Norwegian through:
  • Adding and managing vocabulary
  • Chatting with an AI tutor (GPT)
  • Practicing pronunciation and fluency (Whisper + GPT feedback)

 Visual overview:
- Opens with a friendly onboarding screen (shown once)
- Sidebar gives connection info and access to “Getting Started”
- Three main activity sections: Vocabulary, AI Dialogue, Speech Practice
"""

# ============================================================
#  IMPORTS
# ------------------------------------------------------------
# Streamlit builds the UI. `requests` talks to the FastAPI backend.
# We *try* to load a mic recorder component for speech practice; if it
# fails, the rest of the app still works (text-only mode).
# `SequenceMatcher` is used locally for simple text similarity (UI hints).
# ============================================================

import streamlit as st
import requests
from difflib import SequenceMatcher

# Optional: Microphone component (audio recording for speech practice)
try:
    from streamlit_mic_recorder import mic_recorder
    _HAS_REC = True
except Exception as e:
    import traceback
    st.sidebar.write("⚠️ Mic import error:", e)
    st.sidebar.text("".join(traceback.format_exc()))
    _HAS_REC = False


# ============================================================
#  API CONFIGURATION & PAGE SETUP
# ------------------------------------------------------------
# `API_BASE` tells the UI where the backend lives (local or deployed).
# `st.set_page_config` sets the browser tab title/icon/layout.
# ============================================================

# Local development:
API_BASE = "http://localhost:8000"
# Online Deployment :
# API_BASE = "https://norwegian-ai-backend.onrender.com"

st.set_page_config(page_title="Norwegian Language Learning App", page_icon="🇳🇴", layout="centered")


# ============================================================
#  ONBOARDING (WELCOME PAGE)
# ------------------------------------------------------------
# Goal: help first-time users understand the app in 1 minute.
# - Shows once on first load (using st.session_state['seen_intro']).
# - Explains the 3 main features (Vocabulary, AI Dialogue, Speech).
# - User clicks "Continue" to see the rest of the application.
# You can reopen it anytime from the sidebar "Getting Started" button.
# ============================================================

if "seen_intro" not in st.session_state:
    st.session_state.seen_intro = False

# Show onboarding page if user hasn't seen it yet
if not st.session_state.seen_intro:
    st.title("👋 Welcome to the Norwegian Learning App!")
    st.markdown("""
    This app helps you learn and practice Norwegian through three main activities:

    1. **📚 Vocabulary** – Add and review words with examples.  
    2. **💬 AI Dialogue** – Chat naturally with your Norwegian AI tutor.  
    3. **🎙️ Speech Practice** – Record yourself and get pronunciation feedback.  

    ---
     **Try this demo:**  
    - Type `Hei, jeg heter Maria!` in the dialogue section  
    - or say it in Speech Practice to test your pronunciation.

    You can revisit this page anytime from the sidebar.
    """)

    if st.button("🚀 Continue to App"):
        st.session_state.seen_intro = True
        st.rerun()

    st.stop()  # stops rendering the rest of the app until user continues


# ============================================================
#  STYLING
# ------------------------------------------------------------
# Small CSS to make buttons rounded and improve hover states.
# This affects *only* visuals (no app logic).
# ============================================================

st.markdown("""
    <style>
        div.stButton > button:first-child {
            border-radius: 10px;
            background-color: #007bff;
            color: white;
            font-weight: 600;
        }
        div.stButton > button:first-child:hover {
            background-color: #0056b3;
            color: #e6e6e6;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🇳🇴 Norwegian Language Learning App")
st.markdown("Interact with your AI-powered backend (FastAPI + Streamlit).")


# ============================================================
#  SIDEBAR
# ------------------------------------------------------------
# - Shows which backend the app is connected to (useful for debugging).
# - Provides a button to reopen the Onboarding page at any time.
# ============================================================

st.sidebar.caption(f"🌐 Connected to: {API_BASE}")
if st.sidebar.button("ℹ️ Getting Started"):
    st.session_state.seen_intro = False
    st.rerun()


# ============================================================
#  HELPER FUNCTIONS (UI-only helpers)
# ------------------------------------------------------------
# _similarity(a, b): light text similarity measure for UI hints.
# _tone_style(tone): maps feedback "tone" to an emoji + color for cards.
# These helpers are local to the UI; backend does the heavy lifting.
# ============================================================

def _similarity(a: str, b: str) -> float:
    """Simple helper to compare two texts for similarity."""
    a, b = (a or "").lower().strip(), (b or "").lower().strip()
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _tone_style(tone: str):
    """Return an emoji and color for visual tone feedback."""
    tone = tone.lower()
    if tone == "praise":
        return "😊", "#4caf50"
    elif tone == "encouraging":
        return "💪", "#ff9800"
    else:
        return "😐", "#2196f3"


# ============================================================
#  VOCABULARY
# ------------------------------------------------------------
# What users see:
# - "Add a New Word" form: word, translation, category, difficulty, example.
# - "Search & Manage" panel: filter, inline edit, delete with confirmations.
#
# What happens under the hood:
# - POST /vocabulary to add words.
# - GET /vocabulary with optional ,category and difficulty_level= for listing.
# Intent:
# - Give learners control over their personal wordbank.
# - Keep UI snappy: st.rerun() after edits/deletes to refresh the list.
# ============================================================

st.header("📚 Vocabulary")
st.subheader("Add a New Word")

# Input fields for adding new vocabulary
word = st.text_input("Enter a Norwegian word:")
translation = st.text_input("Enter its English translation:")
category = st.selectbox(
    "Category",
    ["noun", "verb", "adjective", "greeting", "daily_life", "healthcare", "shopping", "other"]
)
difficulty = st.slider("Difficulty level", 1, 5, 1)
example_sentence = st.text_area("Example sentence (optional):")

# --- Submit button ---
if st.button("Add Vocabulary"):
    data = {
        "norwegian_word": word,
        "english_translation": translation,
        "category": category,
        "difficulty_level": difficulty,
        "example_sentence": example_sentence
    }
    res = requests.post(f"{API_BASE}/vocabulary", json=data)
    if res.status_code == 201:
        st.success("✅ Word added successfully!")
    else:
        st.error(f"❌ Error: {res.text}")


# --- View & Manage Vocabulary ---
st.subheader("Search & Manage Vocabulary")

if "show_vocab" not in st.session_state:
    st.session_state.show_vocab = False

toggle_label = "📂 Show Vocabulary List" if not st.session_state.show_vocab else "📁 Hide Vocabulary List"
if st.button(toggle_label):
    st.session_state.show_vocab = not st.session_state.show_vocab

if st.session_state.show_vocab:
    search_term = st.text_input("🔍 Search word or translation")
    selected_category = st.selectbox("Filter by category", ["all", "noun", "verb", "adjective", "greeting", "daily_life", "healthcare", "shopping", "other"])
    selected_difficulty = st.slider("Filter by difficulty", 1, 5, 1)

    params = {}
    if selected_category != "all":
        params["category"] = selected_category
    if selected_difficulty:
        params["difficulty_level"] = selected_difficulty

    res = requests.get(f"{API_BASE}/vocabulary", params=params)
    if res.status_code == 200:
        vocab_list = res.json()
        if search_term:
            vocab_list = [
                v for v in vocab_list
                if search_term.lower() in v["norwegian_word"].lower()
                or search_term.lower() in v["english_translation"].lower()
            ]

        if vocab_list:
            st.markdown(f"**Found {len(vocab_list)} words**")
            for v in vocab_list:
                with st.expander(f"{v['norwegian_word']} → {v['english_translation']}"):
                    st.write(f"**Category:** {v['category']}")
                    st.write(f"**Difficulty:** {v['difficulty_level']}")
                    st.write(f"**Example:** {v.get('example_sentence', '') or '–'}")

                    # Inline editing UI
                    new_translation = st.text_input(f"Edit translation for '{v['norwegian_word']}'", v["english_translation"], key=f"edit_{v['id']}")
                    new_example = st.text_area(f"Edit example for '{v['norwegian_word']}'", v.get("example_sentence", ""), key=f"example_{v['id']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_{v['id']}"):
                            update_data = {"english_translation": new_translation, "example_sentence": new_example}
                            update_res = requests.put(f"{API_BASE}/vocabulary/{v['id']}", json=update_data)
                            if update_res.status_code == 200:
                                st.success("✅ Updated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Update failed.")
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{v['id']}"):
                            del_res = requests.delete(f"{API_BASE}/vocabulary/{v['id']}")
                            if del_res.status_code == 200:
                                st.warning("🗑️ Deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Delete failed.")
        else:
            st.info("No words found with the current filters.")
    else:
        st.error("❌ Could not load vocabulary.")
else:
    st.caption("Click the button above to view or hide your saved vocabulary list.")


# ============================================================
# AI DIALOGUE PRACTICE
# ------------------------------------------------------------
# What users see:
# - A simple chat window storing the conversation (session_state).
# - A difficulty selector (beginner/intermediate/advanced).
#
# What happens under the hood:
# - POST /ai/dialogue with {message, difficulty_level}.
# - The backend prompts GPT to reply in Norwegian and provide an English line.
# - "Reset Chat" clears server memory and local session history.
#
# Intent:
# - Practice natural conversation.
# - Difficulty influences how simple/complex the AI’s language is.
# ============================================================

st.header("💬 AI Dialogue Practice")
st.subheader("Chat with your AI Tutor")

# Display previous chat messages
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")

# Input area
user_input = st.text_input("Write something to the AI (in English or Norwegian):")
difficulty = st.selectbox("Select difficulty:", ["beginner", "intermediate", "advanced"])

# Send message to backend
if st.button("Send"):
    if user_input.strip():
        payload = {"message": user_input, "difficulty_level": difficulty}
        res = requests.post(f"{API_BASE}/ai/dialogue", json=payload)
        if res.status_code == 200:
            reply = res.json()
            norwegian = reply["norwegian"]
            english = reply["english"]
            st.session_state.chat_history.append(("🧑 You", user_input))
            st.session_state.chat_history.append(("🤖 AI", f"{norwegian}\n*{english}*"))
            st.rerun()
        else:
            st.error("❌ AI endpoint not responding.")
    else:
        st.warning("Please type something first.")

if st.button("🔄 Reset Chat"):
    try:
        requests.post(f"{API_BASE}/ai/dialogue/reset")
    except Exception:
        pass
    st.session_state.chat_history = []
    st.success("Chat cleared.")
    st.rerun()


# ============================================================
# ️ SPEECH PRACTICE
# ------------------------------------------------------------
# 3 modes in tabs:
# 1) "Repeat after me" — record mic and compare vs expected sentence.
# 2) "Upload recording" — upload an audio file and compare vs expected.
# 3) "Speak freely" — record mic without a target; AI gives general feedback.

# Visuals:
# - Feedback cards with emoji + color for tone ("praise", "encouraging", etc.).
# ============================================================

st.header("🎙️ Speech Practice")

# Tabs visually separate the three modes
tabs = st.tabs(["🗣 Repeat after me", "📂 Upload recording", "💬 Speak freely"])

# ----------------------------
#  TAB 1 — REPEAT AFTER ME
# ----------------------------
# UX:
# - User records audio, types a target sentence
# - Clicks "Check Pronunciation" to send both to the backend.
#
# Backend:
# - POST /ai/speech/pronunciation with form-data (audio + expected_text).
# - Backend uses Whisper to transcribe and GPT to craft feedback.
#
# UI feedback:
# - Card shows Accuracy %, Feedback text, and a "Semantic" note.
# - We also show "Expected" vs "Heard" so learners see exact differences.

with tabs[0]:
    st.markdown("Practice by repeating a sentence to test your pronunciation and meaning.")

    if _HAS_REC:
        audio_data = mic_recorder(start_prompt="🎙️ Start recording", stop_prompt="🛑 Stop recording", just_once=False, use_container_width=True)
        if audio_data:
            st.audio(audio_data["bytes"], format="audio/wav")
            expected_text = st.text_input("Sentence to practice:", placeholder="For example: Jeg liker å spise mat")

            if st.button("✅ Check Pronunciation"):
                if not expected_text.strip():
                    st.warning("💡 Please enter a sentence first.")
                    st.stop()

                files = {"audio": ("mic.wav", audio_data["bytes"], "audio/wav")}
                data = {"expected_text": expected_text}
                res = requests.post(f"{API_BASE}/ai/speech/pronunciation", files=files, data=data)

                if res.status_code == 200:
                    r = res.json()
                    acc = r.get("accuracy", 0)
                    feedback = r.get("feedback", "")
                    tone = r.get("emotion_tone", "neutral")
                    semantic = r.get("semantic_comment", "")
                    emoji, color = _tone_style(tone)

                    # 🟩 Feedback card
                    st.markdown("---")
                    st.markdown(
                        f"""
                        <div style="background:{color};border-radius:1rem;padding:1rem 1.5rem;color:white;font-size:1.1rem;box-shadow:0 4px 12px rgba(0,0,0,0.25);">
                            <p style="margin:0;">{emoji} <b>Accuracy:</b> {acc:.0%}</p>
                            <p style="margin:0;">💬 <b>Feedback:</b> {feedback}</p>
                            <p style="margin:0;">🧠 <b>Semantic:</b> {semantic}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.progress(min(max(acc, 0.0), 1.0))
                    st.markdown(f"**Expected:** {r['expected']}  \n**Heard:** {r['heard']}")
                else:
                    st.error("❌ Pronunciation check failed.")
    else:
        st.warning("The mic component couldn’t be loaded. Install streamlit-mic-recorder or refresh.")


# ----------------------------
# TAB 2 — UPLOAD RECORDING
# ----------------------------
# UX:
# - User uploads WAV/MP3 and types the target sentence they attempted.
# - Clicks "Check Pronunciation (upload)" to analyze.
#
# Backend:
# - Same endpoint as Tab 1: /ai/speech/pronunciation.
#
# UI feedback:
# - Same visual card + progress bar pattern for consistency.

with tabs[1]:
    st.markdown("Upload a recording for transcription and pronunciation feedback.")
    uploaded_file = st.file_uploader("Upload Norwegian speech (WAV or MP3)", type=["wav", "mp3"])
    expected_text = st.text_input("Sentence you tried to say:")

    if st.button("✅ Check Pronunciation (upload)"):
        if uploaded_file and expected_text:
            files = {"audio": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            data = {"expected_text": expected_text}
            res = requests.post(f"{API_BASE}/ai/speech/pronunciation", files=files, data=data)

            if res.status_code == 200:
                r = res.json()
                acc = r.get("accuracy", 0)
                feedback = r.get("feedback", "")
                tone = r.get("emotion_tone", "neutral")
                semantic = r.get("semantic_comment", "")
                emoji, color = _tone_style(tone)

                # 🎧 Feedback card (same style as mic version)
                st.markdown("---")
                st.markdown(
                    f"""
                    <div style="background:{color};border-radius:1rem;padding:1rem 1.5rem;color:white;font-size:1.1rem;box-shadow:0 4px 12px rgba(0,0,0,0.25);">
                        <p style="margin:0;">{emoji} <b>Accuracy:</b> {acc:.0%}</p>
                        <p style="margin:0;">💬 <b>Feedback:</b> {feedback}</p>
                        <p style="margin:0;">🧠 <b>Semantic:</b> {semantic}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(max(acc, 0.0), 1.0))
                st.markdown(f"**Expected:** {r['expected']}  \n**Heard:** {r['heard']}")
            else:
                st.error("❌ Failed to analyze the recording.")
        else:
            st.warning("Please upload an audio file and enter a sentence first.")


# ----------------------------
#  TAB 3 — SPEAK FREELY
# ----------------------------
# UX:
# - User records any Norwegian speech (no expected sentence).
#
# Backend:
# - POST /ai/speech/free_feedback with the audio file.
# - Backend transcribes and asks GPT to rate fluency and comment.
#
# UI feedback:
# - Shows what Whisper heard (so users can spot errors).
# - Card presents Fluency %, a short comment, and a semantic tip.

with tabs[2]:
    st.markdown("Speak naturally — the AI will analyze your pronunciation, fluency, emotion, and meaning.")

    if _HAS_REC:
        free_audio = mic_recorder(start_prompt="🎙️ Start speaking", stop_prompt="🛑 Stop", just_once=False, use_container_width=True)
        if free_audio:
            st.audio(free_audio["bytes"], format="audio/wav")

            if st.button("💬 Get AI Feedback"):
                files = {"audio": ("free.wav", free_audio["bytes"], "audio/wav")}
                res = requests.post(f"{API_BASE}/ai/speech/free_feedback", files=files)

                if res.status_code == 200:
                    r = res.json()
                    acc = r.get("accuracy", 0)
                    feedback = r.get("feedback", "")
                    tone = r.get("emotion_tone", "neutral")
                    semantic = r.get("semantic_comment", "")
                    heard = r.get("heard", "(no transcript)")
                    emoji, color = _tone_style(tone)

                    st.markdown("---")
                    st.success("🗣️ You said:")
                    st.markdown(
                        f"<div style='background-color:#1e1e1e;padding:0.8rem 1rem;border-radius:0.5rem;color:#ddd;font-style:italic;'>{heard}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Feedback card with fluency bar
                    st.markdown(
                        f"""
                        <div style="background:{color};border-radius:1rem;padding:1rem 1.5rem;color:white;font-size:1.05rem;box-shadow:0 4px 12px rgba(0,0,0,0.25);">
                            <p style="margin:0;">{emoji} <b>Fluency Score:</b> {acc:.0%}</p>
                            <p style="margin:0;">💬 <b>Feedback:</b> {feedback}</p>
                            <p style="margin:0;">🧠 <b>Semantic:</b> {semantic}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.progress(min(max(acc, 0.0), 1.0))
                else:
                    st.error("❌ Could not get feedback. Try again.")
    else:
        st.warning("⚠️ Microphone not available. Try reinstalling 'streamlit-mic-recorder' or refreshing the page.")