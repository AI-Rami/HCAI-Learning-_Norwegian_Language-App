import os
import time
import json
import requests
import streamlit as st

# =========================
# Configuration
# =========================
# Prefer st.secrets for deployment; fallback to env; else manual input widget.
API_BASE = (
    st.secrets.get("API_BASE")
    if hasattr(st, "secrets") else os.getenv("API_BASE")
) or "https://YOUR-FASTAPI-URL.example.com"

st.set_page_config(page_title="Norwegian HCAI Tutor", page_icon="🇳🇴", layout="wide")

# ---------- Small helper wrappers ----------
def _url(path: str) -> str:
    return f"{API_BASE.rstrip('/')}{path}"

def get(path: str, **kwargs):
    try:
        r = requests.get(_url(path), timeout=30, **kwargs)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def post(path: str, json=None, files=None, data=None, **kwargs):
    try:
        r = requests.post(_url(path), json=json, files=files, data=data, timeout=60, **kwargs)
        # Some endpoints (file upload) may return non-JSON on failure, so try to decode but be robust
        try:
            payload = r.json()
        except Exception:
            payload = {"raw": r.text}
        if r.status_code >= 400:
            return None, payload.get("detail") or payload
        return payload, None
    except Exception as e:
        return None, str(e)

def put(path: str, json=None, **kwargs):
    try:
        r = requests.put(_url(path), json=json, timeout=30, **kwargs)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        try:
            return None, r.json().get("detail")
        except Exception:
            return None, str(e)

# =========================
# Sidebar: API & User
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    api_base_input = st.text_input("API base URL", value=API_BASE, help="Your deployed FastAPI URL")
    if api_base_input and api_base_input != API_BASE:
        API_BASE = api_base_input  # live-switch during session

    st.divider()
    st.markdown("## 👤 User")

    # Load users
    users_payload, err = get("/users")
    if err:
        st.error(f"Could not load users: {err}")
        users_payload = []

    usernames = [u["username"] for u in users_payload] if users_payload else []
    selected_username = st.selectbox("Select user", options=["— choose —"] + usernames, index=0)

    new_user = st.text_input("Or create new username")
    if st.button("Create user"):
        if not new_user.strip():
            st.warning("Please type a username.")
        else:
            created, err = post("/users", json={"username": new_user.strip()})
            if err:
                st.error(f"Create failed: {err}")
            else:
                st.success(f"User created: {created['username']}")
                time.sleep(0.6)
                st.rerun()

    # Keep current user in session
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
        st.session_state.username = None

    if selected_username != "— choose —":
        # Find id
        uid = None
        for u in users_payload:
            if u["username"] == selected_username:
                uid = u["id"]
                break
        st.session_state.user_id = uid
        st.session_state.username = selected_username

    # Status
    if st.session_state.user_id:
        st.success(f"Active user: {st.session_state.username} (id={st.session_state.user_id})")
    else:
        st.info("No active user selected yet.")

# =========================
# Header
# =========================
st.title("🇳🇴 Norwegian Language Learning — HCAI")
st.caption("High human control + high automation: transparent lessons, speech practice, and progress tracking.")

# =========================
# Tabs
# =========================
tab_home, tab_lessons, tab_vocab, tab_dialogue, tab_pron, tab_progress = st.tabs(
    ["🏠 Home", "📘 Lessons", "🗂️ Vocabulary", "💬 Dialogue", "🎤 Pronunciation", "📊 Progress"]
)

# ---------- HOME ----------
with tab_home:
    colL, colR = st.columns([1, 2])
    with colL:
        st.subheader("API Health")
        health, err = get("/health")
        if err:
            st.error(f"Health check failed: {err}")
        else:
            st.json(health)

        st.subheader("Stats")
        stats, err = get("/stats")
        if err:
            st.error(f"Stats failed: {err}")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("👥 Users", stats.get("total_users", 0))
            c2.metric("📚 Vocabulary", stats.get("total_vocabulary", 0))
            c3.metric("📘 Lessons", stats.get("total_lessons", 0))
            c4.metric("✅ Progress entries", stats.get("total_progress_entries", 0))

    with colR:
        st.subheader("Categories")
        cats, err = get("/categories")
        if err:
            st.error(f"Categories failed: {err}")
        else:
            st.json(cats)

# ---------- LESSONS ----------
with tab_lessons:
    st.subheader("Browse lessons")
    # Filters
    q_category = st.text_input("Filter by category (optional)", value="")
    q_diff = st.slider("Filter by difficulty (optional)", 0, 5, 0, help="0 = no filter")
    params = {}
    if q_category.strip():
        params["category"] = q_category.strip()
    if q_diff != 0:
        params["difficulty_level"] = q_diff

    lessons, err = get("/lessons", params=params)
    if err:
        st.error(f"Load lessons failed: {err}")
    else:
        if not lessons:
            st.info("No lessons found.")
        else:
            selected = st.selectbox(
                "Select a lesson",
                options=[f"#{l['id']} — {l['title']} (level {l['difficulty_level']}, {l['category']})" for l in lessons]
            )
            selected_id = int(selected.split("—")[0].replace("#", "").strip()) if selected else None

            # Show details
            if selected_id:
                detail, err = get(f"/lessons/{selected_id}")
                if err:
                    st.error(f"Lesson details failed: {err}")
                else:
                    st.markdown(f"### {detail['title']}")
                    st.caption(f"Category: {detail['category']} • Difficulty: {detail['difficulty_level']}")
                    st.write(detail["description"])
                    st.markdown("#### Content")
                    st.code(detail["content"].strip(), language="markdown")

                    # Save progress (requires user)
                    if st.session_state.user_id:
                        st.markdown("#### Mark as Completed")
                        score = st.slider("Your score for this lesson", 0, 100, 90)
                        if st.button("Save progress for this lesson"):
                            payload = {
                                "user_id": st.session_state.user_id,
                                "lesson_id": selected_id,
                                "completed": 1,
                                "score": float(score),
                            }
                            saved, err = post("/progress", json=payload)
                            if err:
                                st.error(f"Save failed: {err}")
                            else:
                                st.success("Progress saved.")
                    else:
                        st.info("Select a user (left sidebar) to save progress.")

# ---------- VOCABULARY ----------
with tab_vocab:
    st.subheader("Vocabulary")
    vcat = st.text_input("Filter by category", value="")
    vdiff = st.slider("Difficulty", 0, 5, 0)
    params = {}
    if vcat.strip():
        params["category"] = vcat.strip()
    if vdiff != 0:
        params["difficulty_level"] = vdiff

    vocab, err = get("/vocabulary", params=params)
    if err:
        st.error(f"Load vocabulary failed: {err}")
    else:
        if not vocab:
            st.info("No vocabulary found for this filter.")
        else:
            st.dataframe(
                [
                    {
                        "ID": v["id"],
                        "Norwegian": v["norwegian_word"],
                        "English": v["english_translation"],
                        "Category": v["category"],
                        "Level": v["difficulty_level"],
                        "Pronounce": v.get("pronunciation_guide") or "",
                        "Example": v.get("example_sentence") or "",
                    }
                    for v in vocab
                ],
                use_container_width=True
            )

# ---------- DIALOGUE (GPT) ----------
with tab_dialogue:
    st.subheader("Dialogue practice (GPT)")
    if st.session_state.user_id is None:
        st.info("Select a user first.")
    else:
        difficulty = st.select_slider("Difficulty", options=["beginner", "intermediate", "advanced"], value="beginner")
        user_msg = st.text_area("Your message (Norwegian or English is fine)", "Hei! Jeg heter Rami.")
        if st.button("Send"):
            with st.spinner("Thinking…"):
                resp, err = post("/ai/dialogue", json={"message": user_msg, "difficulty_level": difficulty})
            if err:
                st.error(f"Dialogue failed: {err}")
            else:
                st.markdown("**Norwegian:**")
                st.success(resp.get("norwegian", ""))
                st.markdown("**English:**")
                st.info(resp.get("english", ""))
                st.caption(resp.get("explanation", ""))

        if st.button("Reset conversation"):
            done, err = post("/ai/dialogue/reset")
            if err:
                st.error(err)
            else:
                st.success(done.get("message", "Reset."))

# ---------- PRONUNCIATION ----------
with tab_pron:
    st.subheader("Pronunciation practice (Whisper)")
    exp = st.text_input("Expected text (what you try to say)", value="Hei")
    audio = st.file_uploader("Upload audio (wav/mp3/m4a…)", type=["wav", "mp3", "m4a"])
    colA, colB = st.columns(2)

    with colA:
        if st.button("Check pronunciation"):
            if not audio:
                st.warning("Please upload audio first.")
            else:
                files = {"audio": (audio.name, audio.getvalue(), "application/octet-stream")}
                data = {"expected_text": exp}
                with st.spinner("Analyzing…"):
                    result, err = post("/ai/speech/pronunciation", files=files, data=data)
                if err:
                    st.error(f"Pronunciation failed: {err}")
                else:
                    st.metric("Accuracy", f"{round(result['accuracy'] * 100, 1)}%")
                    st.write("**Feedback:**", result["feedback"])
                    st.write("**Expected:**", result["expected"])
                    st.write("**Heard:**", result["heard"])

    with colB:
        if st.button("Transcribe only"):
            if not audio:
                st.warning("Please upload audio first.")
            else:
                files = {"audio": (audio.name, audio.getvalue(), "application/octet-stream")}
                with st.spinner("Transcribing…"):
                    tr, err = post("/ai/speech/transcribe", files=files)
                if err:
                    st.error(f"Transcription failed: {err}")
                else:
                    st.code(tr.get("text", ""), language="text")

    st.divider()
    tip_word = st.text_input("Get pronunciation tips for a word", value="bok")
    if st.button("Get tips"):
        tips, err = get(f"/ai/speech/tips/{tip_word}")
        if err:
            st.error(f"Tips failed: {err}")
        else:
            st.info(tips.get("tips", ""))

# ---------- PROGRESS ----------
with tab_progress:
    st.subheader("Your progress")
    if st.session_state.user_id is None:
        st.info("Select a user to view progress.")
    else:
        progress, err = get("/progress", params={"user_id": st.session_state.user_id})
        if err:
            st.error(f"Load progress failed: {err}")
        else:
            if not progress:
                st.info("No progress yet. Complete a lesson to create an entry.")
            else:
                # Show table
                st.dataframe(
                    [
                        {
                            "ID": p["id"],
                            "Lesson": p["lesson_id"],
                            "Completed": "Yes" if p["completed"] else "No",
                            "Score": p["score"],
                            "Last accessed": p["last_accessed"],
                        }
                        for p in progress
                    ],
                    use_container_width=True
                )

                # Update a row (simple editor)
                st.markdown("#### Update a progress entry")
                ids = [p["id"] for p in progress]
                if ids:
                    pid = st.selectbox("Progress ID", ids)
                    new_score = st.slider("New score", 0, 100, 95)
                    comp = st.selectbox("Completed?", ["No", "Yes"], index=1)
                    if st.button("Update progress"):
                        payload = {
                            "score": float(new_score),
                            "completed": 1 if comp == "Yes" else 0
                        }
                        updated, err = put(f"/progress/{pid}", json=payload)
                        if err:
                            st.error(f"Update failed: {err}")
                        else:
                            st.success("Updated.")
                            time.sleep(0.4)
                            st.rerun()

# Footer
st.caption("© HCAI Norwegian Tutor — Backend: FastAPI, Frontend: Streamlit")
