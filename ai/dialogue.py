"""
dialogue.py
------------
AI module for Norwegian language tutoring (GPT-based).

 Purpose:
Provides a conversational Norwegian tutor powered by OpenAI GPT models.
It detects when the user writes in Norwegian, corrects grammar,
and replies with translations and short tips — adapting to learner difficulty.

Structure:
  1. Imports and setup
  2. Class NorwegianDialogueAI
     • Initialization and API setup
     • Message handling and difficulty adjustment
     • Language detection (Norwegian vs. English)
     • Response generation with structured format
"""

# ============================================================
#  IMPORTS & SETUP
# ------------------------------------------------------------
# os — for environment variables (API key)
# logging — to record GPT responses or errors
# re — used for quick detection of Norwegian characters/words
# OpenAI — official Python SDK for GPT calls
# dotenv — loads the API key from .env file
# ============================================================

import os
import logging
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (expects OPENAI_API_KEY in .env)
load_dotenv()
logging.basicConfig(level=logging.INFO)


# ============================================================
#  CLASS: NorwegianDialogueAI
# ------------------------------------------------------------
# This class wraps GPT so that it behaves like a Norwegian language tutor.
# Key features:
#   • Grammar correction for Norwegian text
#   • English translation and short grammar explanations
#   • Adaptive difficulty (Beginner / Intermediate / Advanced)
#   • Detects if input is Norwegian or English
# ============================================================

class NorwegianDialogueAI:
    """GPT-based Norwegian tutor with grammar correction and conversational flow."""

    def __init__(self):
        """Initialize OpenAI client and set up API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in environment.")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Conversation memory (keeps recent messages)
        self.chat_history = []

    # ------------------------------------------------------------
    #  Reset chat memory
    # ------------------------------------------------------------
    def reset(self):
        """Clear chat memory — useful when user presses 'Reset Chat'."""
        self.chat_history = []

    # ------------------------------------------------------------
    #  Quick language check
    # ------------------------------------------------------------
    def _looks_norwegian(self, text: str) -> bool:
        """
        Detect if input text is likely Norwegian.
        - Looks for Norwegian letters (æ, ø, å)
        - Or counts common Norwegian words
        """
        text_lower = text.lower()

        # If special letters appear — very likely Norwegian
        if re.search(r"[æøå]", text_lower):
            return True

        # Otherwise count common Norwegian words
        common_words = ["jeg", "du", "vi", "og", "ikke", "kan", "har", "mat", "det", "er", "på", "om"]
        count = sum(word in text_lower.split() for word in common_words)
        return count >= 2  # at least two matches = likely Norwegian


    def generate_response(self, user_message: str, difficulty: str = "beginner") -> str:
        """
        Generate AI tutor reply with grammar correction and explanation.
        Automatically detects if input is Norwegian or English and adapts reply.
        """
        is_norwegian = self._looks_norwegian(user_message)

        # ============================================================
        #  SYSTEM PROMPT — defines GPT's role and tone
        # ------------------------------------------------------------
        # GPT behaves as a friendly tutor.
        # Replies differ depending on whether the user wrote in Norwegian or English.
        # Difficulty setting changes how much English support the AI provides.
        # ============================================================

        if is_norwegian:
            # The learner wrote in Norwegian → provide correction + feedback
            system_prompt = (
                "You are an experienced and supportive Norwegian language tutor helping learners improve "
                "their grammar, fluency, and confidence through dialogue.\n\n"
                "When the learner writes in Norwegian, always reply using the exact structure below:\n\n"
                "📝 **Correction (Norwegian):** Rewrite the learner’s sentence correctly. "
                "Keep it simple and clear — show proper word order and grammar.\n"
                "💬 **AI (Norwegian):** Respond naturally in Norwegian using one or two short sentences, "
                "as if continuing a real conversation.\n"
                "_Add the English translation below in italics._\n"
                "💡 **Tip (English):** Briefly explain one grammar or vocabulary point that will help the learner "
                "improve next time. Keep it concise and kind.\n\n"
                "Use tone that feels human, patient, and encouraging.\n"
                "Adapt your reply to the learner’s level:\n"
                "- **Beginner:**  short, simple Norwegian + clear English translation + gentle correction.\n"
                "- **Intermediate:** Mostly Norwegian, English only for hard phrases. Correct naturally.\n"
                "- **Advanced:** Use fluent Norwegian with cultural or idiomatic notes instead of grammar tips.\n\n"
                f"The learner’s current level is: {difficulty}."
            )
        else:
            # The learner wrote in English → translate and respond in Norwegian
            system_prompt = (
                "You are a Norwegian language tutor. "
                "The learner has written in English — reply by translating into Norwegian and include "
                "the English version below in italics.\n"
                "Do not add corrections or grammar notes in this case.\n"
                f"Keep your answer at the language complexity of a {difficulty} learner."
            )

        # ------------------------------------------------------------
        #  Maintain short conversation memory (for context)
        # ------------------------------------------------------------
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        # Add latest user message
        self.chat_history.append({"role": "user", "content": user_message})

        # ------------------------------------------------------------
        #  Send to GPT and return the structured reply
        # ------------------------------------------------------------
        try:
            messages = [{"role": "system", "content": system_prompt}] + self.chat_history

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.5,
                max_tokens=400,
            )

            reply_text = response.choices[0].message.content.strip()

            # Add assistant reply to memory
            self.chat_history.append({"role": "assistant", "content": reply_text})

            logging.info(f"GPT reply: {reply_text}")
            return reply_text

        except Exception as e:
            # Handles network errors or invalid responses
            logging.error(f"GPT API error: {e}")
            return (
                "Beklager, jeg kan ikke svare akkurat nå.\n"
                "Sorry, I can't reply right now. (offline fallback)"
            )


if __name__ == "__main__":
    ai = NorwegianDialogueAI()
    while True:
        text = input("You: ")
        if text.lower() in {"exit", "quit"}:
            break
        print("\n" + ai.generate_response(text, "beginner") + "\n")
