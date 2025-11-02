"""
seed_data.py
-------------
Populates the Norwegian Learning App database with sample vocabulary data.

 Purpose:
Inserts a few basic Norwegian words with English translations and examples.
Used once during setup to create a small starting dataset.


"""

# ============================================================
#  IMPORTS
# ------------------------------------------------------------
# - database: for the Vocabulary model and session
# ============================================================

from database import SessionLocal, Vocabulary, init_db


# ============================================================
#  DATABASE SETUP
# ------------------------------------------------------------
# Ensures that norwegian_app.db exists and has the Vocabulary table.
# Then opens a session for inserting data.
# ============================================================

init_db()
db = SessionLocal()


# ============================================================
#  ADD SAMPLE VOCABULARY DATA
# ------------------------------------------------------------
# Each entry includes:
#   - Norwegian word
#   - English translation
#   - Category and difficulty level
#   - Optional example sentence
# ============================================================

vocab_samples = [
    Vocabulary(
        norwegian_word="hei",
        english_translation="hello",
        category="greeting",
        difficulty_level=1,
        example_sentence="Hei! Hvordan går det?"
    ),
    Vocabulary(
        norwegian_word="takk",
        english_translation="thank you",
        category="greeting",
        difficulty_level=1,
        example_sentence="Takk for hjelpen!"
    ),
    Vocabulary(
        norwegian_word="mat",
        english_translation="food",
        category="noun",
        difficulty_level=1,
        example_sentence="Jeg liker å spise mat."
    ),
    Vocabulary(
        norwegian_word="snakke",
        english_translation="to speak",
        category="verb",
        difficulty_level=2,
        example_sentence="Jeg liker å snakke norsk."
    ),
]


# ============================================================
#  COMMIT DATA
# ------------------------------------------------------------
# Adds all vocabulary items to the database, saves, and closes.
# ============================================================

db.add_all(vocab_samples)
db.commit()
db.close()

print("🎉 Vocabulary seeding completed successfully (norwegian_app.db)")
