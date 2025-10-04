"""
Example usage of the Norwegian Language Learning API
This script demonstrates how to interact with the API endpoints
"""
import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Helper function to print API responses"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def main():
    print("🇳🇴 Norwegian Language Learning API - Example Usage")
    print("="*60)
    
    # 1. Get API Info
    response = requests.get(f"{BASE_URL}/")
    print_response("API Information", response)
    
    # 2. Get Vocabulary (filtered by category)
    response = requests.get(f"{BASE_URL}/vocabulary", params={"category": "greetings", "limit": 3})
    print_response("Vocabulary - Greetings Category", response)
    
    # 3. Get a specific lesson
    response = requests.get(f"{BASE_URL}/lessons/1")
    print_response("Lesson Details - Introduction to Greetings", response)
    
    # 4. Create a new user
    new_user = {"username": f"learner_{requests.utils.quote('test')}"}
    response = requests.post(f"{BASE_URL}/users", json=new_user)
    if response.status_code == 201:
        print_response("Create New User", response)
        user_id = response.json()["id"]
    else:
        print(f"\nUser might already exist, using user_id=1")
        user_id = 1
    
    # 5. Track progress for a lesson
    progress_data = {
        "user_id": user_id,
        "lesson_id": 1,
        "completed": 1,
        "score": 85.5
    }
    response = requests.post(f"{BASE_URL}/progress", json=progress_data)
    if response.status_code == 201:
        print_response("Track Lesson Progress", response)
        progress_id = response.json()["id"]
    
    # 6. Practice dialogue with AI
    dialogue_request = {
        "message": "Hei! Jeg heter John.",
        "difficulty_level": "beginner"
    }
    response = requests.post(f"{BASE_URL}/ai/dialogue", json=dialogue_request)
    print_response("AI Dialogue Practice", response)
    
    # 7. Get practice topic
    response = requests.get(f"{BASE_URL}/ai/dialogue/topic/healthcare")
    print_response("Practice Topic - Healthcare", response)
    
    # 8. Get pronunciation tips
    response = requests.get(f"{BASE_URL}/ai/speech/tips/god morgen")
    print_response("Pronunciation Tips", response)
    
    # 9. Get overall statistics
    response = requests.get(f"{BASE_URL}/stats")
    print_response("Overall Statistics", response)
    
    # 10. Get categories
    response = requests.get(f"{BASE_URL}/categories")
    print_response("Available Categories", response)
    
    print(f"\n{'='*60}")
    print("✅ All API calls completed successfully!")
    print("🌐 Visit http://localhost:8000/docs for interactive API documentation")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Please make sure the server is running:")
        print("  python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
