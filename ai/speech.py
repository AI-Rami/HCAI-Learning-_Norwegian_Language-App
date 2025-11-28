"""
speech.py
----------
AI Speech Processing Module for the Norwegian Language App

Purpose:

This module handles everything related to speech input and pronunciation feedback.
It listens to what the learner says, transcribes it to text using OpenAI Whisper,
compares it with the expected sentence, and generates feedback using GPT.

Main features:
1. Convert recorded audio into text (transcription)
2. Compare spoken vs. expected text to measure pronunciation accuracy
3. Estimate speech speed (words per second)
4. Ask GPT for friendly, detailed pronunciation feedback
5. Highlight correctly/incorrectly pronounced words

Structure:
1. Imports and dependency setup
2. Helper functions for comparing and measuring speech
3. The WhisperSpeechToText class:
   - Setup and initialization
   - Audio transcription with Whisper
   - Pronunciation analysis pipeline
   - GPT-based feedback generation
   - Highlighting of correct/incorrect words
"""


# IMPORTS

# os: Access environment variables (like the OpenAI API key)
# difflib: Compare two strings for similarity
# io: Used for reading files in buffered format
# pydub: Estimate audio length and speech pace
# openai: Used to connect to Whisper and GPT models


import os
from difflib import SequenceMatcher
from io import BufferedReader

# Try loading pydub for audio duration
try:
    from pydub import AudioSegment
    _HAS_PYDUB = True
except Exception:
    _HAS_PYDUB = False

# Try the new OpenAI SDK first
try:
    from openai import OpenAI
    _HAS_OPENAI_NEW = True
except Exception:
    _HAS_OPENAI_NEW = False

# Fallback for older setups (legacy OpenAI library)
try:
    import openai as openai_legacy
    _HAS_OPENAI_LEGACY = True
except Exception:
    _HAS_OPENAI_LEGACY = False



# HELPER FUNCTIONS

# These support pronunciation analysis by measuring similarity
# and estimating speaking pace.


def _similarity(a: str, b: str) -> float:
    """
    Compare two sentences and return how similar they are (0–1).

    Method:
      - Clean and lowercase both strings.
      - Compute base character similarity using difflib.
      - Add a small bonus for exact word matches.

    The result represents how close the learner’s spoken text
    is to the expected text. (1.0 = identical)
    """
    a_clean = (a or "").strip().lower()
    b_clean = (b or "").strip().lower()
    if not a_clean and not b_clean:
        return 1.0
    if not a_clean or not b_clean:
        return 0.0

    base = SequenceMatcher(None, a_clean, b_clean).ratio()

    # Reward for matching words (e.g., correct order or key terms)
    a_words = a_clean.split()
    b_words = b_clean.split()
    if a_words and b_words:
        common = sum(1 for w in a_words if w in b_words)
        word_bonus = 0.1 * (common / max(len(a_words), 1))
        return min(1.0, base * 0.9 + word_bonus)
    return base


def _estimate_speech_speed_seconds(audio_path: str) -> float | None:
    """
    Estimate how long the audio clip lasts (in seconds).

    Used to judge whether the learner spoke too quickly or slowly.


    Returns:
        float: duration in seconds, or None if estimation failed.
    """
    if not _HAS_PYDUB:
        return None
    try:
        audio = AudioSegment.from_file(audio_path)
        return float(len(audio)) / 1000.0  # convert ms → seconds
    except Exception:
        return None



# CLASS: WhisperSpeechToText

# Core class that does all speech processing:
#   - Converts audio to text (Whisper)
#   - Compares text with expected sentence
#   - Calculates accuracy and speed
#   - Uses GPT to provide personalized feedback


class WhisperSpeechToText:
    """
    Speech helper that:
      1. Transcribes audio using Whisper.
      2. Measures how close the spoken text is to the expected one.
      3. Requests GPT to generate teacher-style pronunciation feedback.
    """

    def __init__(self):
        """
        Setup the OpenAI client using the stored API key.

        The constructor:
          - Checks if OPENAI_API_KEY is available.
          - Prefers the new OpenAI SDK, falls back to legacy if needed.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OPENAI_API_KEY not found in environment.")

        # Initialize client (new or legacy)
        self.client = None
        if _HAS_OPENAI_NEW:
            self.client = OpenAI(api_key=self.api_key)
        elif _HAS_OPENAI_LEGACY:
            openai_legacy.api_key = self.api_key
        else:
            raise Exception("OpenAI client not found. Install the 'openai' package.")


    # AUDIO to  TEXT

    def transcribe_audio(self, temp_audio_path: str, language: str = "no") -> str:
        """
        Converts audio into text using OpenAI Whisper.

        Steps:
          1. Ensures the audio file is in 16-bit, 16kHz WAV format for better accuracy.
          2. Sends the file to Whisper for transcription.
          3. Returns the clean transcribed text in Norwegian.

        Arguments:
          - temp_audio_path: local path to the audio file.
          - language: 'no' for Norwegian (default).
        """
        if language.lower() in ["norwegian", "norsk"]:
            language = "no"

        # Try re-encoding audio for consistency
        try:

            audio = AudioSegment.from_file(temp_audio_path)
            audio = audio.set_frame_rate(16000).set_sample_width(2)
            audio.export(temp_audio_path, format="wav")
        except Exception as e:
            print(f"[Audio re-encode skipped] {e}")

        # Send audio to Whisper model
        try:
            if self.client is not None:
                with open(temp_audio_path, "rb") as f:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=BufferedReader(f),
                        response_format="text",
                        language=language,
                        prompt="Clear Norwegian sentences about daily life, hobbies, work, and study."
                    )
                return str(transcript).strip()
            else:
                with open(temp_audio_path, "rb") as audio_file:
                    transcript = openai_legacy.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text",
                        language=language,
                        prompt="Clear Norwegian sentences about daily life, hobbies, work, and study."
                    )
                return str(transcript).strip()
        except Exception as e:
            print(f"[Whisper error] {e}")
            return f"[Transcription failed: {e}]"


    # SPEECH SPEED COMMENT

    @staticmethod
    def _speed_comment(expected_text: str, seconds: float | None) -> str | None:
        """
        Returns a short note about how fast or slow the user spoke.
        Uses words per second (WPS) as a simple pace measure.
        """
        if seconds is None or seconds <= 0:
            return None
        words = max(1, len((expected_text or '').split()))
        wps = words / seconds
        if wps > 3.0:
            return "You spoke quite fast — try slowing down a bit."
        if wps < 1.2:
            return "You spoke very slowly — try a more natural pace."
        return "Nice pace."


    # FULL PRONUNCIATION ANALYSIS

    def analyze_pronunciation(self, expected_text: str, temp_audio_path: str) -> dict:
        """
        Full pipeline for pronunciation evaluation.

        Steps performed:
          1. Transcribe the audio using Whisper.
          2. Compare transcription to expected sentence (accuracy score).
          3. Estimate how long the speech took.
          4. Ask GPT to write feedback like a real teacher.
          5. Return all results in one dictionary.
        """
        transcribed_text = self.transcribe_audio(temp_audio_path)

        # Handle Whisper failure gracefully
        if transcribed_text.startswith("[Transcription failed:"):
            return {
                "accuracy": 0.0,
                "feedback": "Transcription failed. Please try again.",
                "expected": expected_text,
                "heard": transcribed_text,
                "speed_comment": None,
                "highlights_html": None,
                "gpt_feedback": None,
            }

        # Step 1 — Compare similarity
        accuracy = _similarity(expected_text, transcribed_text)

        # Step 2 — Estimate speaking pace
        seconds = _estimate_speech_speed_seconds(temp_audio_path)
        speed_comment = self._speed_comment(expected_text, seconds)

        # Step 3 — Ask GPT for professional feedback
        gpt_feedback = None
        try:
            accuracy_percent = round(accuracy * 100, 1)
            msg = (
                "You are a professional Norwegian language tutor and pronunciation coach. "
                "The student was asked to repeat a specific Norwegian sentence.\n\n"
                f" Target sentence (expected): {expected_text}\n"
                f" Heard (transcribed by Whisper): {transcribed_text}\n"
                f" Similarity score: {accuracy_percent}%\n\n"
                "Give feedback in this structure:\n"
                "1️. Norwegian Feedback: 2–3 sentences in Norwegian — supportive and clear.\n"
                "2️. English Translation: Translate your feedback to English.\n"
                "3️. Detailed Evaluation (English): Comment briefly on pronunciation, grammar, and meaning.\n"
                "4️. Practical Tips: Up to 3 short, specific tips for improvement.\n\n"
                "Keep tone friendly and encouraging — max 8–10 sentences."
            )

            resp = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.5,
                max_tokens=350,
                messages=[
                    {"role": "system", "content": "You are a professional Norwegian tutor. Be supportive but exact."},
                    {"role": "user", "content": msg},
                ],
            )
            gpt_feedback = resp.choices[0].message.content.strip()

        except Exception as e:
            print(f"[GPT feedback skipped] {e}")

        # Step 4 — Highlight correct and incorrect words
        highlights_html = self._highlight_words(expected_text, transcribed_text)

        # Step 5 — Final structured result
        return {
            "accuracy": round(float(accuracy), 4),
            "feedback": (
                "Utmerket uttale – det hørtes naturlig ut!"
                if accuracy >= 0.9 else
                "Bra innsats – det meste er riktig, men litt mer tydelighet hjelper."
                if accuracy >= 0.75 else
                "Nesten riktig, prøv å uttale tydeligere og gjenta setningen roligere."
            ),
            "expected": expected_text,
            "heard": transcribed_text,
            "speed_comment": speed_comment,
            "highlights_html": highlights_html,
            "gpt_feedback": gpt_feedback,
        }


    # WORD HIGHLIGHT VISUALIZATION

    @staticmethod
    def _highlight_words(expected: str, heard: str) -> str:
        """
        Creates simple HTML markup to color correct words (green)
        and incorrect or missing ones (red).
        This visual aid can be shown in the frontend.
        """
        exp = (expected or "").strip().split()
        got = (heard or "").strip().split()
        got_set = set(got)

        buf = []
        for w in exp:
            if w in got_set:
                buf.append(f"<span style='color:#2e7d32;font-weight:600'>{w}</span>")
            else:
                buf.append(f"<span style='color:#c62828;font-weight:600'>{w}</span>")
        return " ".join(buf)
