"""
ai/dialogue.py

Norwegian conversation generator using OpenAI GPT-3.5-turbo (new API client).
Requires environment variable OPENAI_API_KEY.

Class:
    NorwegianDialogueAI:
        - generate_response(user_message, difficulty="easy"): Gets Norwegian reply and English translation.
"""

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)


class NorwegianDialogueAI:
    """
    Generates conversational Norwegian replies using OpenAI GPT-3.5-turbo.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
        # Initialize client
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, user_message: str, difficulty: str = "easy") -> str:
        """
        Sends user message and difficulty to GPT-3.5-turbo.
        The prompt instructs GPT to act as a Norwegian tutor, reply in Norwegian,
        then provide a concise English translation.

        Args:
            user_message (str): The user's input/message.
            difficulty (str): Difficulty level (easy, medium, hard).

        Returns:
            str: Tutor's response.
        """
        prompt = (
            f"You are a friendly Norwegian language tutor for learners. "
            f"Reply in Norwegian first, then provide an English translation on a new line. "
            f"Adjust complexity for difficulty level: {difficulty}. "
            f"User: {user_message}"
        )

        logging.info("Calling GPT-3.5-turbo for Norwegian dialogue")

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Norwegian language tutor. Respond in Norwegian, "
                            "then provide a clear English translation on the next line."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=250,
            )

            reply_text = response.choices[0].message.content.strip()
            logging.info(f"GPT reply: {reply_text}")
            return reply_text

        except Exception as e:
            logging.error(f"GPT API error: {e}")
            return (
                "Beklager, jeg kan ikke svare akkurat nå.\n"
                "Sorry, I can't reply right now. (offline fallback)"
            )


# Example for quick test
if __name__ == "__main__":
    ai = NorwegianDialogueAI()
    print(ai.generate_response("Hei! Hvordan har du det?", difficulty="easy"))
