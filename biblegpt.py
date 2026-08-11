import os
import json
import random
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Do NOT crash the entire Flask application if the API key
# is missing. The AI functions will report the problem instead.
client = None

if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Bible CSV is expected to be in the same directory as this file.
BIBLE_DATA_FILE = BASE_DIR / "bible_data_set.csv"

# Vercel's filesystem is not persistent between deployments/
# invocations. /tmp is writable during a function execution.
SAVED_VERSES_FILE = Path("/tmp/saved_verses.json")


# ---------------------------------------------------------
# Load Bible dataset
# ---------------------------------------------------------

try:
    bible_df = pd.read_csv(BIBLE_DATA_FILE)
except Exception as e:
    bible_df = pd.DataFrame(columns=["citation", "text"])
    print(f"Warning: Could not load Bible dataset: {e}")


# ---------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------

MODEL_NAME = "gemini-2.5-flash"


def get_ai_client():
    """
    Return the Gemini client when the API key is available.
    """
    if client is None:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. "
            "Add GOOGLE_API_KEY to the Vercel environment variables."
        )

    return client


# ---------------------------------------------------------
# Save generated verse
# ---------------------------------------------------------

def save_verse(verse):
    try:
        if SAVED_VERSES_FILE.exists():
            with open(SAVED_VERSES_FILE, "r", encoding="utf-8") as f:
                saved_verses = json.load(f)
        else:
            saved_verses = []

        saved_verses.append(verse)

        with open(SAVED_VERSES_FILE, "w", encoding="utf-8") as f:
            json.dump(saved_verses, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Warning: Could not save verse: {e}")


# ---------------------------------------------------------
# Get random Bible verse
# ---------------------------------------------------------

def get_random_verse():
    if bible_df.empty:
        return "Bible dataset is unavailable."

    verse = bible_df.sample(1).iloc[0]

    return f"{verse['citation']} - {verse['text']}"


# ---------------------------------------------------------
# Search Bible verses
# ---------------------------------------------------------

def search_verse(keyword):
    if bible_df.empty:
        return "Bible dataset is unavailable."

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


# ---------------------------------------------------------
# Generate Bible-style verse
# ---------------------------------------------------------

def generate_bible_style_verse(prompt):
    try:
        ai_client = get_ai_client()

        full_prompt = (
            "Write a poetic Bible-style verse in King James English "
            f"about: {prompt}"
        )

        response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )

        verse = (response.text or "").strip()

        if not verse:
            return "The AI did not return a verse."

        save_verse(verse)

        return verse

    except Exception as e:
        print(f"Gemini generation error: {e}")
        return f"Error generating verse: {str(e)}"


# ---------------------------------------------------------
# Extract topic and find related scriptures
# ---------------------------------------------------------

def get_scriptures_about_topic(question):
    try:
        ai_client = get_ai_client()

        topic_prompt = (
            "Extract the main topic someone is asking about in this "
            "question:\n"
            f"'{question}'\n\n"
            "Respond with only one or two keywords such as "
            "'faith', 'love', or 'forgiveness'."
        )

        topic_response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=topic_prompt
        )

        topic = (topic_response.text or "").strip().lower()

        if not topic:
            return "I couldn't identify a scripture topic."

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
        print(f"Scripture topic error: {e}")
        return f"Error processing question: {str(e)}"
