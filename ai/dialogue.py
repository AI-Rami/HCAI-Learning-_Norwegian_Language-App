"""
Norwegian dialogue practice using AI language models.
This module provides conversational AI for practicing Norwegian.
"""
import os
from typing import Optional


class NorwegianDialogueAI:
    """
    AI-powered Norwegian dialogue practice assistant.
    Helps users practice conversational Norwegian with context-aware responses.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
    
    def generate_response(self, user_message: str, difficulty_level: str = "beginner") -> dict:
        """
        Generate a Norwegian language response for dialogue practice.
        
        Args:
            user_message: The user's input in Norwegian or English
            difficulty_level: beginner, intermediate, or advanced
            
        Returns:
            dict with 'response' (Norwegian text), 'translation' (English), and 'explanation'
        """
        # Store conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Simulated response for now - in production, this would use OpenAI API
        # Example structure for when API is integrated:
        """
        try:
            import openai
            openai.api_key = self.api_key
            
            system_prompt = f'''You are a helpful Norwegian language tutor. 
            Respond in Norwegian at a {difficulty_level} level. 
            After your Norwegian response, provide an English translation and brief explanation.
            Format: NORWEGIAN: [response] | ENGLISH: [translation] | TIP: [helpful tip]'''
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_history
                ]
            )
            
            ai_message = response.choices[0].message.content
            # Parse the response
            ...
        except Exception as e:
            return self._fallback_response(user_message, difficulty_level)
        """
        
        return self._fallback_response(user_message, difficulty_level)
    
    def _fallback_response(self, user_message: str, difficulty_level: str) -> dict:
        """
        Fallback responses when AI API is not available.
        Provides basic conversational responses for common scenarios.
        """
        responses = {
            "beginner": {
                "hei": {
                    "norwegian": "Hei! Hvordan har du det?",
                    "english": "Hi! How are you?",
                    "explanation": "'Hvordan har du det?' is a common greeting meaning 'How are you?'"
                },
                "default": {
                    "norwegian": "Jeg forstår. Kan du si mer om det?",
                    "english": "I understand. Can you say more about that?",
                    "explanation": "This is a simple way to continue the conversation."
                }
            },
            "intermediate": {
                "default": {
                    "norwegian": "Det er interessant! Fortell meg mer om dine tanker.",
                    "english": "That's interesting! Tell me more about your thoughts.",
                    "explanation": "Use 'tanker' for thoughts and 'fortell' to ask someone to tell you something."
                }
            },
            "advanced": {
                "default": {
                    "norwegian": "Jeg setter pris på ditt perspektiv. Kan du utdype det videre?",
                    "english": "I appreciate your perspective. Can you elaborate further?",
                    "explanation": "'Å sette pris på' means to appreciate, and 'utdype' means to elaborate."
                }
            }
        }
        
        user_lower = user_message.lower()
        level_responses = responses.get(difficulty_level, responses["beginner"])
        
        # Check for specific greetings
        for key in level_responses:
            if key in user_lower:
                response = level_responses[key]
                self.conversation_history.append({"role": "assistant", "content": response["norwegian"]})
                return response
        
        # Default response
        response = level_responses["default"]
        self.conversation_history.append({"role": "assistant", "content": response["norwegian"]})
        return response
    
    def reset_conversation(self):
        """Clear conversation history to start fresh."""
        self.conversation_history = []
    
    def get_practice_topic(self, category: str) -> dict:
        """
        Generate a practice dialogue topic based on category.
        
        Args:
            category: Topic category (e.g., 'greetings', 'shopping', 'healthcare')
            
        Returns:
            dict with scenario description and starter phrases
        """
        topics = {
            "greetings": {
                "scenario": "Practice introducing yourself and basic greetings",
                "starters": [
                    "Hei, jeg heter... (Hi, my name is...)",
                    "Hvordan har du det? (How are you?)",
                    "Hyggelig å møte deg! (Nice to meet you!)"
                ]
            },
            "shopping": {
                "scenario": "Practice shopping at a Norwegian store",
                "starters": [
                    "Hvor mye koster dette? (How much does this cost?)",
                    "Jeg leter etter... (I'm looking for...)",
                    "Kan jeg få hjelp? (Can I get help?)"
                ]
            },
            "healthcare": {
                "scenario": "Practice basic healthcare communication",
                "starters": [
                    "Jeg trenger en lege (I need a doctor)",
                    "Jeg føler meg ikke bra (I don't feel well)",
                    "Hvor er legekontoret? (Where is the doctor's office?)"
                ]
            },
            "daily_life": {
                "scenario": "Practice everyday conversation",
                "starters": [
                    "Hva gjør du i dag? (What are you doing today?)",
                    "Jeg må gå til... (I need to go to...)",
                    "Når åpner butikken? (When does the store open?)"
                ]
            }
        }
        
        return topics.get(category, topics["greetings"])
