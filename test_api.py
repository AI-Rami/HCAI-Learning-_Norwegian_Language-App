import requests

BASE_URL = "http://127.0.0.1:8000"

def print_result(name, response, method, endpoint):
    print(f"\n=== {name} ({method} {endpoint}) ===")
    print("Status code:", response.status_code)
    try:
        data = response.json()
        print("Response:", data)
        if 200 <= response.status_code < 300:
            print(f"✅ {name}: OK")
        else:
            print(f"❌ {name}: ERROR")
    except Exception:
        print("Raw:", response.text)
        print(f"❌ {name}: ERROR (response not JSON)")

def test_root():
    endpoint = "/"
    r = requests.get(f"{BASE_URL}{endpoint}")
    print_result("Root Endpoint", r, "GET", endpoint)

def test_health():
    endpoint = "/health"
    r = requests.get(f"{BASE_URL}{endpoint}")
    print_result("Health Check", r, "GET", endpoint)

def test_vocabulary():
    endpoint = "/vocabulary"
    vocab = {
        "norwegian_word": "bok",
        "english_translation": "book",
        "category": "noun",
        "difficulty_level": 1
    }
    r = requests.post(f"{BASE_URL}{endpoint}", json=vocab)
    print_result("Create Vocabulary", r, "POST", endpoint)
    vocab_id = r.json().get("id", 1)

    r = requests.get(f"{BASE_URL}{endpoint}")
    print_result("Get Vocabulary", r, "GET", endpoint)

    r = requests.get(f"{BASE_URL}{endpoint}/{vocab_id}")
    print_result("Get Vocabulary by ID", r, "GET", f"{endpoint}/{vocab_id}")

def test_lessons():
    endpoint = "/lessons"
    lesson = {
        "title": "Introduksjon",
        "description": "Learn greetings",
        "difficulty_level": 1,
        "content": "Hei!",
        "category": "greeting"
    }
    r = requests.post(f"{BASE_URL}{endpoint}", json=lesson)
    print_result("Create Lesson", r, "POST", endpoint)
    lesson_id = r.json().get("id", 1)

    r = requests.get(f"{BASE_URL}{endpoint}")
    print_result("Get Lessons", r, "GET", endpoint)

    r = requests.get(f"{BASE_URL}{endpoint}/{lesson_id}")
    print_result("Get Lesson by ID", r, "GET", f"{endpoint}/{lesson_id}")

    return lesson_id

def test_users():
    endpoint = "/users"
    user = {"username": "testuser"}
    r = requests.post(f"{BASE_URL}{endpoint}", json=user)
    print_result("Create User", r, "POST", endpoint)
    user_id = r.json().get("id", 1)

    r = requests.get(f"{BASE_URL}{endpoint}")
    print_result("Get Users", r, "GET", endpoint)

    r = requests.get(f"{BASE_URL}{endpoint}/{user_id}")
    print_result("Get User by ID", r, "GET", f"{endpoint}/{user_id}")

    return user_id

def test_progress(user_id, lesson_id):
    endpoint = "/progress"
    progress = {
        "user_id": user_id,
        "lesson_id": lesson_id,
        "completed": 1,
        "score": 90.0
    }
    r = requests.post(f"{BASE_URL}{endpoint}", json=progress)
    print_result("Create Progress", r, "POST", endpoint)
    progress_id = r.json().get("id", 1)

    r = requests.get(f"{BASE_URL}{endpoint}")
    print_result("Get All Progress", r, "GET", endpoint)

    r = requests.get(f"{BASE_URL}{endpoint}/{progress_id}")
    print_result("Get Progress by ID", r, "GET", f"{endpoint}/{progress_id}")

    update = {"completed": 1, "score": 95.0}
    r = requests.put(f"{BASE_URL}{endpoint}/{progress_id}", json=update)
    print_result("Update Progress", r, "PUT", f"{endpoint}/{progress_id}")

def test_ai_dialogue():
    endpoint = "/ai/dialogue"
    req = {"message": "Hei! Hvordan har du det?", "difficulty_level": "beginner"}
    r = requests.post(f"{BASE_URL}{endpoint}", json=req)
    print_result("AI Dialogue", r, "POST", endpoint)

    r = requests.post(f"{BASE_URL}/ai/dialogue/reset")
    print_result("AI Dialogue Reset", r, "POST", "/ai/dialogue/reset")

    r = requests.get(f"{BASE_URL}/ai/dialogue/topic/greeting")
    print_result("AI Dialogue Topic", r, "GET", "/ai/dialogue/topic/greeting")

def test_ai_speech():
    audio_path = "sample_audio.wav"
    endpoint_transcribe = "/ai/speech/transcribe"
    endpoint_pronunciation = "/ai/speech/pronunciation"
    endpoint_tips = "/ai/speech/tips/bok"

    try:
        with open(audio_path, "rb") as audio_file:
            files = {"audio": (audio_path, audio_file, "audio/wav")}
            r = requests.post(f"{BASE_URL}{endpoint_transcribe}", files=files)
            print_result("AI Speech Transcribe", r, "POST", endpoint_transcribe)
    except FileNotFoundError:
        print(f"\n[AI Speech Transcribe] Audio file '{audio_path}' not found. Skipping.")

    try:
        with open(audio_path, "rb") as audio_file:
            files = {"audio": (audio_path, audio_file, "audio/wav")}
            data = {"expected_text": "Hei"}
            r = requests.post(f"{BASE_URL}{endpoint_pronunciation}", files=files, data=data)
            print_result("AI Speech Pronunciation", r, "POST", endpoint_pronunciation)
    except FileNotFoundError:
        print(f"\n[AI Speech Pronunciation] Audio file '{audio_path}' not found. Skipping.")

    r = requests.get(f"{BASE_URL}{endpoint_tips}")
    print_result("AI Speech Tips", r, "GET", endpoint_tips)

def test_categories_and_stats():
    r = requests.get(f"{BASE_URL}/categories")
    print_result("Categories", r, "GET", "/categories")
    r = requests.get(f"{BASE_URL}/stats")
    print_result("Stats", r, "GET", "/stats")

def main():
    test_root()
    test_health()
    test_vocabulary()
    lesson_id = test_lessons()
    user_id = test_users()
    test_progress(user_id, lesson_id)
    test_ai_dialogue()
    test_ai_speech()
    test_categories_and_stats()

if __name__ == "__main__":
    main()