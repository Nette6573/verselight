import os
import json

import pandas as pd
from dotenv import load_dotenv
from google import genai


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not configured.")

client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-2.5-flash"


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BIBLE_FILE = os.path.join(
    BASE_DIR,
    "bible_data_set.csv"
)

SAVED_VERSES_FILE = os.path.join(
    BASE_DIR,
    "saved_verses.json"
)


# =========================================================
# LOAD BIBLE DATA
# =========================================================

bible_df = pd.read_csv(BIBLE_FILE)


# =========================================================
# SAVE VERSE
# =========================================================

def save_verse(verse):

    try:

        if os.path.exists(SAVED_VERSES_FILE):

            with open(
                SAVED_VERSES_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                saved_verses = json.load(file)

        else:

            saved_verses = []

        saved_verses.append(verse)

        with open(
            SAVED_VERSES_FILE,
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

    except Exception as error:

        print(f"Error saving verse: {error}")

        return False


# =========================================================
# RANDOM VERSE
# =========================================================

def get_random_verse():

    verse = bible_df.sample(1).iloc[0]

    return (
        f"{verse['citation']} - "
        f"{verse['text']}"
    )


# =========================================================
# SEARCH VERSES
# =========================================================

def search_verse(keyword):

    keyword = keyword.strip()

    if not keyword:

        return "Please enter a word or phrase to search for."

    results = bible_df[
        bible_df["text"].str.contains(
            keyword,
            case=False,
            na=False,
            regex=False
        )
    ]

    if results.empty:

        return "No verses found with that keyword."

    verses = results.head(5).apply(
        lambda row:
        f"{row['citation']} - {row['text']}",
        axis=1
    ).tolist()

    return "\n\n".join(verses)


# =========================================================
# GENERATE BIBLE-INSPIRED VERSE
# =========================================================

def generate_bible_style_verse(prompt):

    prompt = prompt.strip()

    if not prompt:

        return "Please enter a topic for your verse."

    full_prompt = f"""
Create a short original Bible-inspired devotional passage
about the following topic:

{prompt}

Guidelines:

- Make it poetic and uplifting.
- Use traditional, timeless language.
- It may have a gentle biblical tone.
- Do NOT claim that it is an actual Bible verse.
- Do NOT invent a Bible citation.
- Do NOT attribute the passage to Scripture.
- Make it clearly original.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )

        verse = response.text.strip()

        if not verse:

            return "Gemini returned an empty response."

        save_verse(verse)

        return verse

    except Exception as error:

        print(
            f"Gemini generation error: {error}"
        )

        return (
            f"Error generating verse: {error}"
        )


# =========================================================
# FIND SCRIPTURES ABOUT A QUESTION
# =========================================================

def get_scriptures_about_topic(question):

    question = question.strip()

    if not question:

        return "Please ask a Bible-related question."

    topic_prompt = f"""
Identify the main Bible topic in this question.

Question:

{question}

Respond with ONLY one or two keywords.

Examples:

"What does the Bible say about loving others?"
love

"How can I trust God during difficult times?"
faith

"What does Scripture say about forgiving people?"
forgiveness
"""

    try:

        topic_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=topic_prompt
        )

        topic = topic_response.text.strip().lower()

        topic = (
            topic
            .replace(".", "")
            .replace(",", "")
        )

        matches = bible_df[
            bible_df["text"].str.contains(
                topic,
                case=False,
                na=False,
                regex=False
            )
        ]

        if matches.empty:

            return (
                "No scriptures found about that topic."
            )

        results = matches.head(5).apply(
            lambda row:
            f"{row['citation']} - {row['text']}",
            axis=1
        ).tolist()

        return "\n\n".join(results)

    except Exception as error:

        print(
            f"Question processing error: {error}"
        )

        return (
            f"Error processing question: {error}"
        )
