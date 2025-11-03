"""
speech.py
----------
AI speech-processing module for the Norwegian Learning App.

Purpose:
Handles pronunciation analysis and feedback for spoken Norwegian.
Uses:
  • OpenAI Whisper — to transcribe speech to text
  • GPT  — to give pronunciation tips and feedback
  • pydub — to estimate speaking speed (tempo)

Structure:
  1. Imports and optional dependencies
  2. Utility functions for similarity, speed, and highlighting
  3. WhisperSpeechToText class:
     - Initialization and client setup
     - Audio transcription
     - Pronunciation analysis (transcribe , compare , feedback)
     - GPT feedback and HTML highlighting
"""

# ============================================================
# IMPORTS
# ------------------------------------------------------------
# - os for environment access and file handling
# - difflib for text similarity
# - io for buffered file reading (used in Whisper upload)
# - pydub for duration and speech speed estimation
# - openai client for transcription and feedback
# ============================================================

import os
from difflib import SequenceMatcher
from io import BufferedReader

# pydub for estimating speech speed (duration)
try:
    from pydub import AudioSegment
    _HAS_PYDUB = True
except Exception:
    _HAS_PYDUB = False

# Try modern OpenAI client
try:
    from openai import OpenAI
    _HAS_OPENAI_NEW = True
except Exception:
    _HAS_OPENAI_NEW = False

# Legacy OpenAI client fallback (for older setups)
try:
    import openai as openai_legacy
    _HAS_OPENAI_LEGACY = True
except Exception:
    _HAS_OPENAI_LEGACY = False


# ============================================================
#  HELPER FUNCTIONS
# Utility functions that support pronunciation analysis:
#   _similarity() — compares two sentences word-by-word
#   _estimate_speech_speed_seconds() — estimates duration
# ============================================================

def _similarity(a: str, b: str) -> float:
    """Compute character + word-level similarity between two sentences."""
    a_clean = (a or "").strip().lower()
    b_clean = (b or "").strip().lower()
    if not a_clean and not b_clean:
        return 1.0
    if not a_clean or not b_clean:
        return 0.0

    # Base character similarity
    base = SequenceMatcher(None, a_clean, b_clean).ratio()

    # Add a small bonus for exact word matches
    a_words = a_clean.split()
    b_words = b_clean.split()
    if a_words and b_words:
        common = sum(1 for w in a_words if w in b_words)
        word_bonus = 0.1 * (common / max(len(a_words), 1))
        return min(1.0, base * 0.9 + word_bonus)
    return base


def _estimate_speech_speed_seconds(audio_path: str) -> float | None:
    """Estimate speech duration (in seconds) using pydub, if available."""
    if not _HAS_PYDUB:
        return None
    try:
        audio = AudioSegment.from_file(audio_path)
        return float(len(audio)) / 1000.0  # convert ms → seconds
    except Exception:
        return None


# ============================================================
#  CLASS: WhisperSpeechToText
# Core class that performs:
#   1. Audio transcription (Whisper)
#   2. Pronunciation accuracy estimation
#   3. GPT feedback and HTML highlighting
# ============================================================

class WhisperSpeechToText:
    """
    Speech helper that:
      - Transcribes audio with Whisper
      - Compares transcribed text vs expected sentence
      - Gives coaching feedback with GPT
        """

    def __init__(self):
        """Initialize OpenAI API client and verify environment setup."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OPENAI_API_KEY not found in environment.")

        # Prefer modern OpenAI client, fallback to legacy if needed
        self.client = None
        if _HAS_OPENAI_NEW:
            self.client = OpenAI(api_key=self.api_key)
        elif _HAS_OPENAI_LEGACY:
            openai_legacy.api_key = self.api_key
        else:
            raise Exception("OpenAI client not found. Install the official 'openai' package.")

    # ------------------------------------------------------------
    #  Transcription using Whisper
    # ------------------------------------------------------------
    def transcribe_audio(self, temp_audio_path: str, language: str = "no") -> str:
        """
        Convert speech to text using OpenAI Whisper.
        - language='no' forces Norwegian transcription
        - Supports mp3, wav, m4a.
        Returns a clean text string.
        """
        if language.lower() in ["norwegian", "norsk"]:
            language = "no"

        #  Ensure 16-bit 16 kHz WAV for stable Whisper results
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(temp_audio_path)
            audio = audio.set_frame_rate(16000).set_sample_width(2)
            audio.export(temp_audio_path, format="wav")
        except Exception as e:
            print(f"[Audio re-encode skipped] {e}")

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

    # ------------------------------------------------------------
    #  Speech speed estimation comment
    # ------------------------------------------------------------
    @staticmethod
    def _speed_comment(expected_text: str, seconds: float | None) -> str | None:
        """Give a human-readable note on speaking pace."""
        if seconds is None or seconds <= 0:
            return None
        words = max(1, len((expected_text or '').split()))
        wps = words / seconds  # words per second
        if wps > 3.0:
            return "You spoke quite fast — try slowing down a bit."
        if wps < 1.2:
            return "You spoke very slowly — try a more natural pace."
        return "Nice pace."

    # ------------------------------------------------------------
    #  Full pronunciation analysis pipeline
    # ------------------------------------------------------------
    def analyze_pronunciation(self, expected_text: str, temp_audio_path: str) -> dict:
        """
        Steps performed:
          1. Transcribe audio to text
          2. Compare transcribed vs. expected (accuracy)
          3. Estimate speed
          4. Ask GPT for short coaching feedback
          5. Build and return structured feedback dict
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

        # Step 1 — Compute accuracy
        accuracy = _similarity(expected_text, transcribed_text)

        # Step 2 — Estimate speed
        seconds = _estimate_speech_speed_seconds(temp_audio_path)
        speed_comment = self._speed_comment(expected_text, seconds)

        # Step 3 — GPT feedback
        gpt_feedback = None
        try:
            accuracy_percent = round(accuracy * 100, 1)

            msg = (
                "You are a professional Norwegian language tutor and pronunciation coach. "
                "The student was asked to repeat a specific Norwegian sentence aloud.\n\n"
                f"🎯 **Target sentence (expected):** {expected_text}\n"
                f"🎙️ **Heard (transcribed by Whisper):** {transcribed_text}\n"
                f"📊 **Similarity score:** {accuracy_percent}% (calculated automatically)\n\n"
                "Evaluate the student's attempt carefully across pronunciation, grammar, and meaning.\n"
                "Then provide feedback in the following structure:\n\n"
                "1️⃣ **Norwegian Feedback:** 2–3 short sentences in Norwegian. Encourage, correct, and model the right form naturally.\n"
                "2️⃣ **English Translation:** Translate your Norwegian feedback into natural English with the same supportive tone.\n"
                "3️⃣ **Detailed Evaluation (English):** Explain briefly:\n"
                "   • Pronunciation — clarity, vowel/consonant accuracy, rhythm, stress, intonation.\n"
                "   • Grammar — word order, missing or wrong forms, small errors.\n"
                "   • Meaning — did the message still make sense?\n"
                "4️⃣ **Practical Tips:** Up to 3 specific practice ideas (repeat slowly, stress key vowels, imitate rhythm, etc.).\n\n"
                "Style guidelines:\n"
                "- Be friendly and concise (max 8–10 sentences total).\n"
                "- Never restate both full sentences; just reference the key words.\n"
                "- Treat this as live teacher feedback: positive but precise."
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

        # Step 4 — Visual highlight (correct words = green, wrong = red)
        highlights_html = self._highlight_words(expected_text, transcribed_text)

        # Step 5 — Return full feedback structure
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



    # ------------------------------------------------------------
    # Word-level highlight generator
    # ------------------------------------------------------------
    @staticmethod
    def _highlight_words(expected: str, heard: str) -> str:
        """
        Create an HTML snippet that colors correct words green and
        missing/incorrect words red — used by the frontend.
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
