import streamlit as st
import requests
import io

# 🌐 Your deployed backend base URL
API_BASE = "http://127.0.0.1:8000"


st.set_page_config(page_title="Norwegian Language Learning App", page_icon="🇳🇴", layout="centered")
st.title("Norwegian Language Learning App")
st.markdown("Interact with your AI-powered backend (FastAPI + Streamlit)")

# -------------------------------
# 📚 Vocabulary Section
# -------------------------------
st.header("📚 Vocabulary")
word = st.text_input("Enter a Norwegian word:")
translation = st.text_input("Enter its English translation:")
category = st.selectbox("Category", ["noun", "verb", "adjective", "greeting", "daily_life", "healthcare", "shopping", "other"])
difficulty = st.slider("Difficulty level", 1, 5, 1)

if st.button("Add Vocabulary"):
    data = {
        "norwegian_word": word,
        "english_translation": translation,
        "category": category,
        "difficulty_level": difficulty
    }
    res = requests.post(f"{API_BASE}/vocabulary", json=data)
    if res.status_code == 201:
        st.success("✅ Word added successfully!")
    else:
        st.error(f"Error: {res.text}")

if st.button("View All Vocabulary"):
    res = requests.get(f"{API_BASE}/vocabulary")
    if res.status_code == 200:
        vocab_list = res.json()
        st.table(vocab_list)
    else:
        st.error("❌ Could not load vocabulary.")

# -------------------------------
# 📖 Lessons Section
# -------------------------------
st.header("📖 Lessons")
if st.button("Show Lessons"):
    res = requests.get(f"{API_BASE}/lessons")
    if res.status_code == 200:
        lessons = res.json()
        st.table(lessons)
    else:
        st.error("❌ Could not load lessons.")

# -------------------------------
# 💬 Dialogue AI Section
# -------------------------------
st.header("💬 AI Dialogue Practice")
prompt = st.text_input("Write something to the AI (in English or Norwegian):")
difficulty = st.selectbox("Select difficulty:", ["beginner", "intermediate", "advanced"])

if st.button("Send to AI"):
    payload = {"message": prompt, "difficulty_level": difficulty}
    res = requests.post(f"{API_BASE}/ai/dialogue", json=payload)
    if res.status_code == 200:
        reply = res.json()
        st.write("**🇳🇴 Norwegian:**", reply["norwegian"])
        st.write("**🇬🇧 English:**", reply["english"])
        st.caption(reply["explanation"])
    else:
        st.error("AI endpoint not responding.")

# -------------------------------
# 🎙️ Speech Section
# -------------------------------
st.header("🎙️ Speech Practice")

uploaded_file = st.file_uploader("Upload your Norwegian speech (WAV or MP3)", type=["wav", "mp3"])
expected_text = st.text_input("Expected phrase (for pronunciation check):")

col1, col2 = st.columns(2)

with col1:
    if st.button("Transcribe Audio"):
        if uploaded_file:
            files = {"audio": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            res = requests.post(f"{API_BASE}/ai/speech/transcribe", files=files)
            if res.status_code == 200:
                st.success("📝 Transcription:")
                st.write(res.json()["text"])
            else:
                st.error("❌ Transcription failed.")
        else:
            st.warning("Please upload an audio file first.")

with col2:
    if st.button("Check Pronunciation"):
        if uploaded_file and expected_text:
            files = {"audio": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            data = {"expected_text": expected_text}
            res = requests.post(f"{API_BASE}/ai/speech/pronunciation", files=files, data=data)
            if res.status_code == 200:
                feedback = res.json()
                st.json(feedback)
            else:
                st.error("❌ Pronunciation check failed.")
        else:
            st.warning("Upload audio and enter the expected text first.")

# -------------------------------
# 📊 Progress Overview
# -------------------------------
st.header("📊 Progress Overview")
if st.button("Get Stats"):
    res = requests.get(f"{API_BASE}/stats")
    if res.status_code == 200:
        st.json(res.json())
    else:
        st.error("❌ Failed to load stats.")
