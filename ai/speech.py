import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env at import time
load_dotenv()

class WhisperSpeechToText:
    """
    Class-based implementation for OpenAI Whisper speech-to-text and pronunciation check.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OPENAI_API_KEY not found in environment.")
        openai.api_key = self.api_key

    def transcribe_audio(self, temp_audio_path):
        """
        Transcribe audio to text using OpenAI Whisper API.
        Supports formats: mp3, wav, m4a, etc.
        Returns the transcribed text.
        """
        try:
            with open(temp_audio_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            print(f"Whisper API error: {e}")
            return f"[Transcription failed: {str(e)}]"

    def check_pronunciation(self, expected_text, temp_audio_path):
        """
        Check pronunciation by comparing expected_text with audio transcription.
        Returns accuracy, feedback, suggestions, expected, and heard text.
        """
        transcribed_text = self.transcribe_audio(temp_audio_path)
        if isinstance(transcribed_text, str) and transcribed_text.startswith("[Transcription failed:"):
            accuracy = 0.0
            feedback = "Transcription failed. Please try again."
            suggestions = []
            heard = transcribed_text
        else:
            accuracy = 1.0 if expected_text.strip().lower() == transcribed_text.strip().lower() else 0.0
            feedback = "Good job!" if accuracy > 0.7 else "Try again, focus on pronunciation."
            suggestions = []
            heard = transcribed_text
        return {
            "accuracy": accuracy,
            "feedback": feedback,
            "suggestions": suggestions,
            "expected": expected_text,
            "heard": heard
        }