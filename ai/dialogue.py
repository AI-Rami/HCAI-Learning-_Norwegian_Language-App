"""
dialogue.py
------------
AI Module: Norwegian Language Dialogue Tutor (GPT-based)
=========================================================
This file handles all conversational interactions between
the learner and the AI tutor.

Purpose:
--------
The goal of this module is to simulate a friendly, helpful
Norwegian teacher who can correct grammar, explain mistakes,
and hold short, supportive conversations in Norwegian.

It automatically detects whether the learner writes in
Norwegian or English and adjusts the response style.

If the message is in Norwegian → it gives:
  - A corrected version of the sentence
  - A natural AI reply (short conversation)
  - A simple grammar or vocabulary tip

If the message is in English → it translates the text and replies
in Norwegian (with English translation below).

Structure:
----------
1. Imports and environment setup
2. Class NorwegianDialogueAI:
   - Initialization (OpenAI setup)
   - Reset chat memory
   - Detect language (English vs. Norwegian)
   - Generate structured GPT replies
"""

# ============================================================
# IMPORTS AND SETUP
# ============================================================
# os — to access environment variables (for API key)
# logging — for saving GPT responses and errors
# re — regular expressions for language detection
# OpenAI — for accessing GPT models (e.g., gpt-4o)
# dotenv — to load .env file containing the OpenAI API key
# ============================================================

import os
import logging
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Basic logging (prints GPT activity and any errors)
logging.basicConfig(level=logging.INFO)


# ============================================================
# CLASS: NorwegianDialogueAI
# ============================================================
# Main class that manages the AI conversation.
# It connects to GPT, handles message flow, detects language,
# and formats structured replies for the app.
# ============================================================

class NorwegianDialogueAI:
    """GPT-based Norwegian language tutor with correction and explanation features."""

    def __init__(self):
        """
        Initialize OpenAI client and setup memory.
        Loads the OpenAI API key from the environment.
        If the key is missing, it raises an error to alert the user.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in environment.")

        # Initialize GPT client
        self.client = OpenAI(api_key=self.api_key)

        # Conversation history (stores recent messages for context)
        self.chat_history = []

    # ------------------------------------------------------------
    # Reset chat memory
    # ------------------------------------------------------------
    def reset(self):
        """
        Clears the chat memory.
        This is useful when the user clicks “Reset Chat” in the app
        to start a new clean conversation.
        """
        self.chat_history = []

    # ------------------------------------------------------------
    # Detect if text is Norwegian
    # ------------------------------------------------------------
    def _looks_norwegian(self, text: str) -> bool:
        """
        Quick rule-based check to see if the text is likely Norwegian.

        It looks for:
          - Norwegian special characters (æ, ø, å)
          - Common Norwegian words (jeg, du, har, ikke, etc.)

        Returns True if the input looks like Norwegian.
        Otherwise, assumes English or another language.
        """
        text_lower = text.lower()

        # Check for unique Norwegian letters
        if re.search(r"[æøå]", text_lower):
            return True

        # Check for frequent Norwegian words
        common_words = ["jeg", "du", "vi", "og", "ikke", "kan", "har", "mat", "det", "er", "på", "om"]
        count = sum(word in text_lower.split() for word in common_words)
        return count >= 2  # at least two matches = likely Norwegian

    # ------------------------------------------------------------
    # Generate AI Response
    # ------------------------------------------------------------
    def generate_response(self, user_message: str, difficulty: str = "beginner") -> str:
        """
        Generate a reply from GPT that fits the learner’s level and language.

        How it works:
        -------------
        1. Detects if the message is written in Norwegian or English.
        2. Builds a GPT “system prompt” that sets the tutor’s tone and rules.
        3. Sends the message and context history to GPT.
        4. Receives a structured answer that includes:
           - Correction (if Norwegian)
           - Translation
           - Grammar tip or feedback
        5. Saves the interaction in chat history.

        Difficulty levels:
        ------------------
        - beginner: simple sentences, English explanations
        - intermediate: mostly Norwegian, with short English help
        - advanced: fluent Norwegian + cultural notes
        """

        # Step 1: Detect language
        is_norwegian = self._looks_norwegian(user_message)

        # Step 2: Build GPT system prompt depending on language type
        if is_norwegian:
            # The learner wrote in Norwegian
            # → provide corrections, short dialogue, and grammar tip
            system_prompt = (
                "You are a kind and experienced Norwegian language tutor helping learners "
                "improve grammar, vocabulary, and confidence through short dialogues.\n\n"
                "When the learner writes in Norwegian, reply using this format:\n\n"
                "📝 **Correction (Norwegian):** Rewrite the learner’s sentence correctly. "
                "Keep it simple and correct any grammar or spelling mistakes.\n"
                "💬 **AI (Norwegian):** Continue the conversation naturally in one or two short sentences.\n"
                "_Add the English translation below in italics._\n"
                "💡 **Tip (English):** Explain briefly one grammar or vocabulary point "
                "that can help the learner next time. Be supportive and positive.\n\n"
                "Adjust your style based on the learner’s level:\n"
                "- Beginner: very short, simple Norwegian with clear English translation.\n"
                "- Intermediate: more Norwegian, English only for difficult parts.\n"
                "- Advanced: fluent Norwegian and cultural/idiomatic notes.\n\n"
                f"The learner’s current level is: {difficulty}."
            )
        else:
            # The learner wrote in English
            # → translate into Norwegian and give the English version below
            system_prompt = (
                "You are a Norwegian language tutor. "
                "The learner has written in English — translate the message into Norwegian, "
                "and then provide the English version below in italics.\n"
                "Do not give grammar corrections here, only translation.\n"
                f"Keep your language at a {difficulty} level."
            )

        # Step 3: Keep conversation memory short (avoid long history)
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        # Add user message to memory
        self.chat_history.append({"role": "user", "content": user_message})

        # Step 4: Send messages to GPT
        try:
            messages = [{"role": "system", "content": system_prompt}] + self.chat_history

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.5,
                max_tokens=400,
            )

            # Extract GPT’s reply as plain text
            reply_text = response.choices[0].message.content.strip()

            # Save AI reply to chat memory
            self.chat_history.append({"role": "assistant", "content": reply_text})

            logging.info(f"GPT reply: {reply_text}")
            return reply_text

        except Exception as e:
            # If GPT fails (no internet, wrong key, etc.)
            logging.error(f"GPT API error: {e}")
            return (
                "Beklager, jeg kan ikke svare akkurat nå.\n"
                "Sorry, I can't reply right now. (offline mode)"
            )


# ============================================================
# MANUAL TESTING (LOCAL)
# ============================================================
# You can run this file directly (python dialogue.py)
# to test GPT conversation in the terminal.
# ============================================================

if __name__ == "__main__":
    ai = NorwegianDialogueAI()
    while True:
        text = input("You: ")
        if text.lower() in {"exit", "quit"}:
            break
        print("\n" + ai.generate_response(text, "beginner") + "\n")
