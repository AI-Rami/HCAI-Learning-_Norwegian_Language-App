"""
ai/dialogue.py

Final version — Norwegian language tutor with:
✅ Multi-turn memory
✅ Grammar correction and explanations
✅ Automatic detection: correct only when input is in Norwegian
✅ Adaptive difficulty levels
"""

import os
import logging
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)


class NorwegianDialogueAI:
    """GPT-based Norwegian tutor with grammar correction and conversational flow."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in environment.")
        self.client = OpenAI(api_key=self.api_key)
        self.chat_history = []

    def reset(self):
        """Clear chat memory."""
        self.chat_history = []

    @staticmethod
    def _looks_norwegian(text: str) -> bool:
        """
        Quick heuristic to detect if input is likely Norwegian.
        Looks for special letters or frequent Norwegian words.
        """
        text_lower = text.lower()
        if re.search(r"[æøå]", text_lower):
            return True
        common_words = ["jeg", "du", "vi", "og", "ikke", "kan", "har", "mat", "det", "er", "på", "om"]
        count = sum(word in text_lower.split() for word in common_words)
        return count >= 2

    def generate_response(self, user_message: str, difficulty: str = "beginner") -> str:
        """
        Generate response with corrections (only if user wrote in Norwegian).
        """
        is_norwegian = self._looks_norwegian(user_message)

        # Base system prompt
        if is_norwegian:
            system_prompt = (
                "You are a supportive Norwegian language tutor. "
                "The learner writes in Norwegian and you help them correct grammar and improve fluency. "
                "Always reply following this structure:\n\n"
                "📝 Correction: [Show the corrected sentence if there are mistakes, "
                "otherwise say 'No mistakes!']\n"
                "💬 AI: [Reply naturally in Norwegian (1–2 sentences), "
                "then include an English translation in italics.]\n"
                "💡 Tip: [Give a short grammar or vocabulary explanation in English "
                "(if there was a mistake), or a cultural/language note if there wasn't.]\n\n"
                "Keep tone friendly and encouraging. "
                "Adjust the difficulty according to the learner's level "
                f"({difficulty})."
            )
        else:
            # For English inputs — just respond and translate
            system_prompt = (
                "You are a Norwegian language tutor. "
                "The learner wrote in English. Reply in Norwegian and provide the English translation. "
                "Do not include correction or grammar notes in this case. "
                f"Keep responses appropriate for {difficulty} learners."
            )

        # Keep short chat memory
        if len(self.chat_history) > 10:
            self.chat_history = self.chat_history[-10:]

        self.chat_history.append({"role": "user", "content": user_message})

        try:
            messages = [{"role": "system", "content": system_prompt}] + self.chat_history

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.6,
                max_tokens=350,
            )

            reply_text = response.choices[0].message.content.strip()
            self.chat_history.append({"role": "assistant", "content": reply_text})

            logging.info(f"GPT reply: {reply_text}")
            return reply_text

        except Exception as e:
            logging.error(f"GPT API error: {e}")
            return (
                "Beklager, jeg kan ikke svare akkurat nå.\n"
                "Sorry, I can't reply right now. (offline fallback)"
            )


# For quick local testing
if __name__ == "__main__":
    ai = NorwegianDialogueAI()
    while True:
        text = input("You: ")
        if text.lower() in {"exit", "quit"}:
            break
        print("\n" + ai.generate_response(text, "beginner") + "\n")
