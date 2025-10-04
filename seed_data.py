"""
Seed script to populate the database with initial Norwegian language learning data.
Run this script to add sample vocabulary, lessons, and users for testing.
"""
from database import SessionLocal, init_db, User, Vocabulary, Lesson
from datetime import datetime


def seed_database():
    """Populate database with sample data"""
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Vocabulary).first() or db.query(Lesson).first():
            print("Database already contains data. Skipping seed.")
            return
        
        print("Adding sample vocabulary...")
        
        # Sample vocabulary words
        vocabulary_data = [
            # Greetings (Level 1)
            {
                "norwegian_word": "Hei",
                "english_translation": "Hi/Hello",
                "category": "greetings",
                "difficulty_level": 1,
                "pronunciation_guide": "hey",
                "example_sentence": "Hei, hvordan har du det?"
            },
            {
                "norwegian_word": "God morgen",
                "english_translation": "Good morning",
                "category": "greetings",
                "difficulty_level": 1,
                "pronunciation_guide": "goo mor-gen",
                "example_sentence": "God morgen! Sov du godt?"
            },
            {
                "norwegian_word": "Takk",
                "english_translation": "Thank you",
                "category": "greetings",
                "difficulty_level": 1,
                "pronunciation_guide": "tahk",
                "example_sentence": "Takk for hjelpen!"
            },
            {
                "norwegian_word": "Ha det",
                "english_translation": "Goodbye",
                "category": "greetings",
                "difficulty_level": 1,
                "pronunciation_guide": "hah deh",
                "example_sentence": "Ha det bra! Sees senere."
            },
            
            # Daily Life (Level 1-2)
            {
                "norwegian_word": "Vann",
                "english_translation": "Water",
                "category": "daily_life",
                "difficulty_level": 1,
                "pronunciation_guide": "vahn",
                "example_sentence": "Kan jeg få et glass vann?"
            },
            {
                "norwegian_word": "Mat",
                "english_translation": "Food",
                "category": "daily_life",
                "difficulty_level": 1,
                "pronunciation_guide": "maht",
                "example_sentence": "Maten er veldig god!"
            },
            {
                "norwegian_word": "Hjelp",
                "english_translation": "Help",
                "category": "daily_life",
                "difficulty_level": 1,
                "pronunciation_guide": "yehlp",
                "example_sentence": "Trenger du hjelp?"
            },
            
            # Healthcare (Level 2)
            {
                "norwegian_word": "Lege",
                "english_translation": "Doctor",
                "category": "healthcare",
                "difficulty_level": 2,
                "pronunciation_guide": "lay-geh",
                "example_sentence": "Jeg må gå til legen."
            },
            {
                "norwegian_word": "Sykehus",
                "english_translation": "Hospital",
                "category": "healthcare",
                "difficulty_level": 2,
                "pronunciation_guide": "syoo-keh-hoos",
                "example_sentence": "Hvor er nærmeste sykehus?"
            },
            {
                "norwegian_word": "Apotek",
                "english_translation": "Pharmacy",
                "category": "healthcare",
                "difficulty_level": 2,
                "pronunciation_guide": "ah-poh-tehk",
                "example_sentence": "Apoteket åpner klokken ni."
            },
            
            # Shopping (Level 2)
            {
                "norwegian_word": "Butikk",
                "english_translation": "Store/Shop",
                "category": "shopping",
                "difficulty_level": 2,
                "pronunciation_guide": "boo-tik",
                "example_sentence": "Butikken er åpen til fem."
            },
            {
                "norwegian_word": "Penger",
                "english_translation": "Money",
                "category": "shopping",
                "difficulty_level": 2,
                "pronunciation_guide": "peng-er",
                "example_sentence": "Hvor mye koster dette? / Jeg har ikke nok penger."
            },
        ]
        
        for vocab_data in vocabulary_data:
            vocab = Vocabulary(**vocab_data)
            db.add(vocab)
        
        print(f"Added {len(vocabulary_data)} vocabulary words.")
        
        # Sample lessons
        print("Adding sample lessons...")
        
        lessons_data = [
            {
                "title": "Introduction to Norwegian Greetings",
                "description": "Learn basic Norwegian greetings and how to introduce yourself",
                "difficulty_level": 1,
                "category": "greetings",
                "content": """
Welcome to your first Norwegian lesson!

In this lesson, you'll learn:
1. How to say hello and goodbye
2. How to introduce yourself
3. Basic polite expressions

Key Phrases:
- Hei! (Hi!)
- God morgen! (Good morning!)
- Jeg heter... (My name is...)
- Hyggelig å møte deg! (Nice to meet you!)
- Takk (Thank you)
- Ha det bra! (Goodbye!)

Practice:
Try introducing yourself using these phrases. Remember, Norwegians are friendly and appreciate when you try to speak their language!
                """
            },
            {
                "title": "Essential Daily Vocabulary",
                "description": "Learn common words and phrases for everyday situations",
                "difficulty_level": 1,
                "category": "daily_life",
                "content": """
Essential words for daily life in Norway:

Food and Drink:
- Mat (Food)
- Vann (Water)
- Kaffe (Coffee)
- Brød (Bread)

Common Verbs:
- Å spise (To eat)
- Å drikke (To drink)
- Å gå (To go/walk)
- Å ha (To have)

Useful Phrases:
- Jeg vil ha... (I would like...)
- Kan jeg få...? (Can I have...?)
- Hvor er...? (Where is...?)

Practice these words by using them in simple sentences!
                """
            },
            {
                "title": "Healthcare Communication",
                "description": "Important vocabulary for healthcare situations",
                "difficulty_level": 2,
                "category": "healthcare",
                "content": """
Healthcare Vocabulary and Phrases:

Key Words:
- Lege (Doctor)
- Sykehus (Hospital)
- Apotek (Pharmacy)
- Medisin (Medicine)

Important Phrases:
- Jeg trenger en lege (I need a doctor)
- Jeg føler meg ikke bra (I don't feel well)
- Jeg har vondt i... (I have pain in...)
- Hvor er legekontoret? (Where is the doctor's office?)

Emergency:
- Hjelp! (Help!)
- Ring ambulanse! (Call an ambulance!)
- Det er en nødsituasjon (It's an emergency)

Remember: In Norway, call 113 for medical emergencies.
                """
            },
            {
                "title": "Shopping and Services",
                "description": "Learn how to shop and use services in Norway",
                "difficulty_level": 2,
                "category": "shopping",
                "content": """
Shopping Vocabulary:

Places:
- Butikk (Store)
- Supermarked (Supermarket)
- Apotek (Pharmacy)
- Bank (Bank)

Money and Payment:
- Penger (Money)
- Kort (Card)
- Kontant (Cash)
- Hvor mye koster dette? (How much does this cost?)

Useful Phrases:
- Jeg leter etter... (I'm looking for...)
- Har dere...? (Do you have...?)
- Kan jeg prøve dette? (Can I try this?)
- Kan jeg betale med kort? (Can I pay with card?)

Opening Hours:
- Åpen (Open)
- Stengt (Closed)
- Når åpner/stenger dere? (When do you open/close?)
                """
            },
        ]
        
        for lesson_data in lessons_data:
            lesson = Lesson(**lesson_data)
            db.add(lesson)
        
        print(f"Added {len(lessons_data)} lessons.")
        
        # Sample users
        print("Adding sample users...")
        
        users_data = [
            {"username": "demo_user"},
            {"username": "test_learner"},
        ]
        
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        
        print(f"Added {len(users_data)} users.")
        
        db.commit()
        print("\n✓ Database seeded successfully!")
        print("\nSample data summary:")
        print(f"  - {len(vocabulary_data)} vocabulary words")
        print(f"  - {len(lessons_data)} lessons")
        print(f"  - {len(users_data)} users")
        print("\nYou can now start the API server with: uvicorn main:app --reload")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
