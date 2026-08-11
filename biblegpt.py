import os
import json
import pandas as pd
from google import genai

# --------------------------------------------------
# Configuration
# --------------------------------------------------

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not configured.")

client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

# --------------------------------------------------
# Bible dataset
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIBLE_FILE = os.path.join(BASE_DIR, "bible_data_set.csv")

bible_df = pd.read_csv(BIBLE_FILE)

# --------------------------------------------------
# Random Bible verse
# --------------------------------------------------

def get_random_verse():
    verse = bible_df.sample(1).iloc[0]

    return f"{verse['citation']} - {verse['text']}"


# --------------------------------------------------
# Search Bible verses
# --------------------------------------------------

def search_verse(keyword):
    keyword = keyword.strip()

    if not keyword:
        return "Please enter a keyword to search."

    results = bible_df[
        bible_df["text"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]

    if results.empty:
        return "No verses found with that keyword."

    verses = results.head(5).apply(
        lambda row: f"{row['citation']} - {row['text']}",
        axis=1
    ).tolist()

    return "\n\n".join(verses)


# --------------------------------------------------
# Generate Bible-style verse
# --------------------------------------------------

def generate_bible_style_verse(prompt):
    prompt = prompt.strip()

    if not prompt:
        return "Please enter a topic for the verse."

    full_prompt = f"""
Write a short, original Bible-inspired verse in a
King James-style tone about the following topic:

{prompt}

Important:
- Do not claim that the verse is an actual Bible verse.
- Do not invent a Bible citation.
- Keep it inspirational and concise.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )

        verse = response.text.strip()

        return verse

    except Exception as e:
        print(f"Gemini generation error: {e}")
        return "Sorry, VerseLight could not generate a verse right now."


# --------------------------------------------------
# Find scriptures related to a question
# --------------------------------------------------

def get_scriptures_about_topic(question):
    question = question.strip()

    if not question:
        return "Please ask a Bible-related question."

    topic_prompt = f"""
Identify the main biblical topic in this question.

Question:
{question}

Return only one or two simple keywords.

Examples:
faith
love
forgiveness
peace
anxiety
marriage
hope
wisdom
fear
strength
"""

    try:
        topic_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=topic_prompt
        )

        topic = topic_response.text.strip().lower()

        matches = bible_df[
            bible_df["text"].str.contains(
                topic,
                case=False,
                na=False
            )
        ]

        if matches.empty:
            return "No scriptures found about that topic."

        results = matches.head(5).apply(
            lambda row: f"{row['citation']} - {row['text']}",
            axis=1
        ).tolist()

        return "\n\n".join(results)

    except Exception as e:
        print(f"Question processing error: {e}")
        return "Sorry, VerseLight could not process your question right now."


# --------------------------------------------------
# Saved verses
# --------------------------------------------------

def save_verse(verse):
    """
    Local-development helper.

    Vercel's normal filesystem is read-only, so this should
    not be treated as permanent storage in production.
    """

    saved_file = "/tmp/saved_verses.json"

    try:
        if os.path.exists(saved_file):
            with open(saved_file, "r", encoding="utf-8") as f:
                saved_verses = json.load(f)
        else:
            saved_verses = []

        saved_verses.append(verse)

        with open(saved_file, "w", encoding="utf-8") as f:
            json.dump(saved_verses, f, indent=4)

        return True

    except Exception as e:
        print(f"Save verse error: {e}")
        return False
