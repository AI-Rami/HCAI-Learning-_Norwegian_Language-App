"""
seed_data.py
-------------
Initial Data Setup Script for the Norwegian Language App
=========================================================

Purpose:
--------
This file fills the database with a few example Norwegian words.
It helps during setup or testing to make sure the app shows
some vocabulary entries right away — so the interface doesn’t start empty.

How it works:
-------------
1. Connects to the existing SQLite database.
2. Ensures that the Vocabulary table exists.
3. Inserts a few sample Norwegian–English word pairs with examples.
4. Commits (saves) the data and closes the database session.

You usually run this file once after creating the database.
"""

# ============================================================
# IMPORTS
# ============================================================
# Imports the database functions and models.
# These allow creating sessions and adding data.
# ============================================================

from database import SessionLocal, Vocabulary, init_db

# ============================================================
# INITIALIZE DATABASE
# ============================================================
# Makes sure the database file and Vocabulary table exist.
# Then creates a session to communicate with the database.
# ============================================================

init_db()
db = SessionLocal()

# ============================================================
# SAMPLE VOCABULARY DATA
# ============================================================
# A few simple Norwegian words to test the app.
# Each word includes:
#   - Norwegian form
#   - English translation
#   - Category (like noun, verb, greeting)
#   - Difficulty level (1–5)
#   - Example sentence for context
# ============================================================

vocab_samples = [
    Vocabulary(
        norwegian_word="hei",
        english_translation="hello",
        category="greeting",
        difficulty_level=1,
        example_sentence="Hei! Hvordan går det?"  # “Hi! How are you?”
    ),
    Vocabulary(
        norwegian_word="takk",
        english_translation="thank you",
        category="greeting",
        difficulty_level=1,
        example_sentence="Takk for hjelpen!"      # “Thanks for your help!”
    ),
    Vocabulary(
        norwegian_word="mat",
        english_translation="food",
        category="noun",
        difficulty_level=1,
        example_sentence="Jeg liker å spise mat."  # “I like to eat food.”
    ),
    Vocabulary(
        norwegian_word="snakke",
        english_translation="to speak",
        category="verb",
        difficulty_level=2,
        example_sentence="Jeg liker å snakke norsk."  # “I like to speak Norwegian.”
    ),
]

# ============================================================
# COMMIT AND CLOSE SESSION
# ============================================================
# Adds all vocabulary entries to the database, saves changes,
# then closes the connection cleanly.
# ============================================================

db.add_all(vocab_samples)
db.commit()
db.close()

print("🎉 Vocabulary seeding completed successfully (norwegian_app.db)")
