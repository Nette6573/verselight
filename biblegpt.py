import os
import json
import pandas as pd
from google import genai


# ============================================================
# Configuration
# ============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

_client = None


def get_ai_client():
    """
    Create the Gemini client only when an AI feature needs it.
    This prevents Gemini configuration problems from crashing
    the entire Flask application at startup.
    """
    global _client

    if _client is not None:
        return _client

    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured.")

    _client = genai.Client(api_key=GOOGLE_API_KEY)

    return _client


# ============================================================
# Bible Dataset
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BIBLE_FILE = os.path.join(
    BASE_DIR,
    "bible_data_set.csv"
)

bible_df = pd.read_csv(BIBLE_FILE)


# ============================================================
# Helper Functions
# ============================================================

def format_verse(row):
    """Format a Bible dataset row for display."""
    return f"{row['citation']} - {row['text']}"


def search_bible_text(keyword, limit=5):
    """Search the Bible dataset for a keyword or phrase."""

    keyword = keyword.strip()

    if not keyword:
        return []

    results = bible_df[
        bible_df["text"].str.contains(
            keyword,
            case=False,
            na=False,
            regex=False
        )
    ]

    return results.head(limit).apply(
        format_verse,
        axis=1
    ).tolist()


# ============================================================
# Random Bible Verse
# ============================================================

def get_random_verse():
    """Return a random Bible verse."""

    verse = bible_df.sample(1).iloc[0]

    return format_verse(verse)


# ============================================================
# Search Bible Verses
# ============================================================

def search_verse(keyword):
    """Search Bible verses by keyword or phrase."""

    keyword = keyword.strip()

    if not keyword:
        return "Please enter a keyword to search."

    verses = search_bible_text(keyword)

    if not verses:
        return "No verses found with that keyword."

    return "\n\n".join(verses)


# ============================================================
# Generate Bible-Style Verse
# ============================================================

def generate_bible_style_verse(topic):
    """
    Generate an original Bible-inspired verse using Gemini.
    The generated text must not be presented as actual Scripture.
    """

    topic = topic.strip()

    if not topic:
        return "Please enter a topic for the verse."

    full_prompt = f"""
Write a short, original Bible-inspired verse about:

{topic}

Style:
- Warm
- Inspirational
- Reflective
- Biblical in tone
- Concise

Important:
- This must be completely original.
- Do NOT claim that it is actual Scripture.
- Do NOT invent a Bible citation.
- Do NOT attribute it to a biblical author.
- Do not use quotation marks around the response.
- Return only the generated verse.
"""

    try:
        client = get_ai_client()

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )

        if not response.text:
            return "Sorry, VerseLight could not generate a verse right now."

        return response.text.strip()

    except Exception as e:
        print(f"Gemini generation error: {repr(e)}")

        return (
            "Sorry, VerseLight could not generate a verse right now. "
            "Please try again."
        )


# ============================================================
# Bible Question / Topic Search
# ============================================================

TOPIC_KEYWORDS = {
    "love": [
        "love",
        "loving",
        "loved"
    ],

    "faith": [
        "faith",
        "believe",
        "belief",
        "trust"
    ],

    "hope": [
        "hope",
        "hopeless"
    ],

    "peace": [
        "peace",
        "peaceful"
    ],

    "fear": [
        "fear",
        "afraid",
        "scared",
        "fearful"
    ],

    "forgiveness": [
        "forgive",
        "forgiveness",
        "forgiving"
    ],

    "strength": [
        "strength",
        "strong",
        "weakness"
    ],

    "wisdom": [
        "wisdom",
        "wise"
    ],

    "prayer": [
        "prayer",
        "pray",
        "praying"
    ],

    "marriage": [
        "marriage",
        "married",
        "husband",
        "wife"
    ],

    "family": [
        "family",
        "children",
        "child",
        "parent",
        "parents"
    ],

    "anger": [
        "anger",
        "angry"
    ],

    "anxiety": [
        "anxiety",
        "anxious",
        "worry",
        "worried"
    ],

    "healing": [
        "healing",
        "heal",
        "sick",
        "illness"
    ],

    "sin": [
        "sin",
        "sinful",
        "temptation",
        "tempted"
    ],

    "purpose": [
        "purpose",
        "calling"
    ]
}


def identify_topic(question):
    """Identify a common biblical topic from a natural-language question."""

    question_lower = question.lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                return topic

    return None


def get_scriptures_about_topic(question):
    """
    Find Bible verses related to a natural-language question.

    This feature does not require Gemini.
    """

    question = question.strip()

    if not question:
        return "Please ask a Bible-related question."

    topic = identify_topic(question)

    # Search for a recognized biblical topic.
    if topic:
        verses = search_bible_text(topic)

        if verses:
            return "\n\n".join(verses)

    # If no known topic was detected, try searching
    # the question itself.
    verses = search_bible_text(question)

    if verses:
        return "\n\n".join(verses)

    return (
        "I couldn't find matching scriptures for that question. "
        "Try asking about love, faith, hope, peace, forgiveness, "
        "prayer, wisdom, strength, or another biblical topic."
    )


# ============================================================
# Saved Verses
# ============================================================

def save_verse(verse):
    """
    Save a verse temporarily.

    Vercel's filesystem is not permanent storage, so this is
    only temporary. Persistent saved verses should eventually
    use a database.
    """

    saved_file = "/tmp/saved_verses.json"

    try:
        if os.path.exists(saved_file):

            with open(
                saved_file,
                "r",
                encoding="utf-8"
            ) as file:

                saved_verses = json.load(file)

        else:
            saved_verses = []

        saved_verses.append(verse)

        with open(
            saved_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                saved_verses,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception as e:

        print(f"Save verse error: {repr(e)}")

        return False
