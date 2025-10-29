import streamlit as st
import requests
import io

# 🌐 Your deployed backend base URL
API_BASE = "https://norwegian-ai-backend.onrender.com"


st.set_page_config(page_title="Norwegian Language Learning App", page_icon="🇳🇴", layout="centered")
st.title("Norwegian Language Learning App")
st.markdown("Interact with your AI-powered backend (FastAPI + Streamlit)")

# -------------------------------
# -------------------------------
# 📚 Vocabulary Section (Upgraded)
# -------------------------------
st.header("📚 Vocabulary")

st.subheader("Add a New Word")

# Input fields
word = st.text_input("Enter a Norwegian word:")
translation = st.text_input("Enter its English translation:")
category = st.selectbox(
    "Category",
    ["noun", "verb", "adjective", "greeting", "daily_life", "healthcare", "shopping", "other"]
)
difficulty = st.slider("Difficulty level", 1, 5, 1)
example_sentence = st.text_area("Example sentence (optional):")

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
        st.error(f"Error: {res.text}")

# --- Filter & Search Section ---
st.subheader("Search & Manage Vocabulary")

search_term = st.text_input("🔍 Search word or translation")
selected_category = st.selectbox(
    "Filter by category", ["all", "noun", "verb", "adjective", "greeting", "daily_life", "healthcare", "shopping", "other"]
)
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
            if search_term.lower() in v["norwegian_word"].lower() or search_term.lower() in v["english_translation"].lower()
        ]

    if vocab_list:
        for v in vocab_list:
            with st.expander(f"{v['norwegian_word']} → {v['english_translation']}"):
                st.write(f"**Category:** {v['category']}")
                st.write(f"**Difficulty:** {v['difficulty_level']}")
                st.write(f"**Example:** {v.get('example_sentence', '') or '–'}")

                # Edit and Delete
                new_translation = st.text_input(f"Edit translation for '{v['norwegian_word']}'", v["english_translation"], key=f"edit_{v['id']}")
                new_example = st.text_area(f"Edit example for '{v['norwegian_word']}'", v.get("example_sentence", ""), key=f"example_{v['id']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"💾 Save Changes", key=f"save_{v['id']}"):
                        update_data = {
                            "english_translation": new_translation,
                            "example_sentence": new_example
                        }
                        update_res = requests.put(f"{API_BASE}/vocabulary/{v['id']}", json=update_data)
                        if update_res.status_code == 200:
                            st.success("✅ Updated successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Update failed.")
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{v['id']}"):
                        del_res = requests.delete(f"{API_BASE}/vocabulary/{v['id']}")
                        if del_res.status_code == 200:
                            st.warning("🗑️ Deleted successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Delete failed.")
    else:
        st.info("No words found with the current filters.")
else:
    st.error("❌ Could not load vocabulary.")


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
