"""
Speech-to-text functionality using OpenAI Whisper for pronunciation feedback.
This module helps users practice Norwegian pronunciation.
"""
import os
import tempfile
from typing import Optional, Tuple
import io


class WhisperSpeechToText:
    """
    Whisper-based speech recognition for Norwegian pronunciation practice.
    Provides transcription and pronunciation feedback.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Size of Whisper model (tiny, base, small, medium, large)
                       'base' is a good balance of speed and accuracy
        """
        self.model_size = model_size
        self.model = None
    
    def load_model(self):
        """Lazy load the Whisper model to save memory."""
        if self.model is None:
            try:
                import whisper
                self.model = whisper.load_model(self.model_size)
            except ImportError:
                raise ImportError(
                    "Whisper not installed. Install with: pip install openai-whisper"
                )
    
    def transcribe_audio(self, audio_file: bytes, language: str = "no") -> dict:
        """
        Transcribe audio to text using Whisper.
        
        Args:
            audio_file: Audio file bytes (MP3, WAV, etc.)
            language: Language code ('no' for Norwegian)
            
        Returns:
            dict with 'text' (transcription), 'language', and 'confidence'
        """
        self.load_model()
        
        # Save audio bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_file)
            temp_audio_path = temp_audio.name
        
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                temp_audio_path,
                language=language,
                task="transcribe"
            )
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "confidence": self._calculate_confidence(result)
            }
        except Exception as e:
            return {
                "text": "",
                "language": language,
                "confidence": 0.0,
                "error": str(e)
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
    
    def _calculate_confidence(self, whisper_result: dict) -> float:
        """
        Calculate confidence score from Whisper result.
        
        Args:
            whisper_result: Raw Whisper transcription result
            
        Returns:
            Confidence score between 0 and 1
        """
        # Whisper doesn't directly provide confidence, so we estimate it
        # based on available metrics
        segments = whisper_result.get("segments", [])
        
        if not segments:
            return 0.5  # Default confidence
        
        # Average the no_speech_prob (inverted) across segments
        total_confidence = 0.0
        for segment in segments:
            no_speech_prob = segment.get("no_speech_prob", 0.5)
            total_confidence += (1.0 - no_speech_prob)
        
        return total_confidence / len(segments) if segments else 0.5
    
    def compare_pronunciation(
        self, 
        expected_text: str, 
        transcribed_text: str
    ) -> dict:
        """
        Compare expected text with transcribed audio for pronunciation feedback.
        
        Args:
            expected_text: The correct Norwegian text
            transcribed_text: What Whisper heard from the audio
            
        Returns:
            dict with 'accuracy', 'feedback', and 'suggestions'
        """
        expected_lower = expected_text.lower().strip()
        transcribed_lower = transcribed_text.lower().strip()
        
        # Calculate simple word-level accuracy
        expected_words = expected_lower.split()
        transcribed_words = transcribed_lower.split()
        
        if not expected_words:
            return {
                "accuracy": 0.0,
                "feedback": "No expected text provided",
                "suggestions": []
            }
        
        # Simple matching algorithm
        matches = sum(1 for word in expected_words if word in transcribed_words)
        accuracy = (matches / len(expected_words)) * 100
        
        # Generate feedback
        if accuracy >= 90:
            feedback = "Excellent pronunciation! Keep up the good work!"
            suggestions = []
        elif accuracy >= 70:
            feedback = "Good job! Your pronunciation is clear with minor improvements needed."
            suggestions = self._find_mismatched_words(expected_words, transcribed_words)
        elif accuracy >= 50:
            feedback = "You're making progress! Focus on these words for better pronunciation."
            suggestions = self._find_mismatched_words(expected_words, transcribed_words)
        else:
            feedback = "Keep practicing! Try speaking more slowly and clearly."
            suggestions = self._find_mismatched_words(expected_words, transcribed_words)
        
        return {
            "accuracy": round(accuracy, 2),
            "feedback": feedback,
            "suggestions": suggestions,
            "expected": expected_text,
            "heard": transcribed_text
        }
    
    def _find_mismatched_words(self, expected: list, transcribed: list) -> list:
        """
        Find words that don't match between expected and transcribed text.
        
        Args:
            expected: List of expected words
            transcribed: List of transcribed words
            
        Returns:
            List of words that need practice
        """
        mismatched = []
        for word in expected:
            if word not in transcribed:
                mismatched.append({
                    "word": word,
                    "tip": f"Practice pronouncing '{word}' more clearly"
                })
        
        return mismatched[:5]  # Return top 5 suggestions
    
    def get_pronunciation_tips(self, word: str) -> dict:
        """
        Get pronunciation tips for a specific Norwegian word.
        
        Args:
            word: Norwegian word to get tips for
            
        Returns:
            dict with pronunciation guidance
        """
        # Common Norwegian pronunciation patterns
        tips = {
            "å": "Pronounced like 'aw' in 'law'",
            "æ": "Pronounced like 'a' in 'cat'",
            "ø": "Pronounced like 'u' in 'burn' (rounded lips)",
            "kj": "Pronounced like 'ch' in German 'ich'",
            "skj": "Pronounced like 'sh' in 'ship'",
            "sj": "Pronounced like 'sh' in 'ship'"
        }
        
        word_lower = word.lower()
        relevant_tips = []
        
        for pattern, tip in tips.items():
            if pattern in word_lower:
                relevant_tips.append(tip)
        
        return {
            "word": word,
            "tips": relevant_tips if relevant_tips else ["Practice this word slowly, focusing on each syllable"],
            "ipa": self._get_ipa_approximation(word)
        }
    
    def _get_ipa_approximation(self, word: str) -> str:
        """
        Get IPA (International Phonetic Alphabet) approximation.
        In production, this would use a proper Norwegian IPA dictionary.
        """
        # Placeholder - in production, use a Norwegian pronunciation dictionary
        return f"[IPA notation for '{word}']"
