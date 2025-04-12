import os
import pandas as pd
import random
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Google API Key is not set. Please check your .env file.")

# Configure the API and initialize the model
genai.configure(api_key=GOOGLE_API_KEY)

# Create the model once and reuse it
try:
    model = genai.GenerativeModel("gemini-1.5-flash")  # You can change to gemini-pro or another
    # Test the model to confirm it's working
    response = model.generate_content("test")
    print(response.text.strip())
except Exception as e:
    raise Exception(f"Error initializing model: {e}")

# Load Bible dataset (assuming the 'bible_data_set.csv' file exists)
bible_df = pd.read_csv('bible_data_set.csv')

# JSON file to save generated verses
SAVED_VERSES_FILE = 'saved_verses.json'

# Save verse to a JSON file
def save_verse(verse):
    if os.path.exists(SAVED_VERSES_FILE):
        with open(SAVED_VERSES_FILE, 'r') as f:
            saved_verses = json.load(f)
    else:
        saved_verses = []

    saved_verses.append(verse)

    with open(SAVED_VERSES_FILE, 'w') as f:
        json.dump(saved_verses, f, indent=4)

# Get a random Bible verse from CSV
def get_random_verse():
    verse = bible_df.sample(1).iloc[0]
    return f"{verse['citation']} - {verse['text']}"

# Search the CSV for a verse by keyword
def search_verse(keyword):
    results = bible_df[bible_df['text'].str.contains(keyword, case=False, na=False)]

    if results.empty:
        return "No verses found with that keyword."

    verses = results.head(5).apply(
        lambda row: f"{row['citation']} - {row['text']}", axis=1
    ).tolist()

    return "\n\n".join(verses)

# Generate a custom Bible-style verse with Gemini
def generate_bible_style_verse(prompt):
    full_prompt = f"Write a poetic Bible-style verse in King James English about: {prompt}"

    try:
        response = model.generate_content(full_prompt)
        verse = response.text.strip()
        save_verse(verse)
        return verse
    except Exception as e:
        return f"Error generating verse: {str(e)}"

# Extract topic-related verses based on natural language question
def get_scriptures_about_topic(question):
    try:
        topic_prompt = (
            f"Extract the main topic someone is asking about in this question:\n"
            f"'{question}'\n"
            f"Respond with only one or two keywords like 'faith', 'love', or 'forgiveness'."
        )
        topic_response = model.generate_content(topic_prompt)
        topic = topic_response.text.strip().lower()

        matches = bible_df[bible_df['text'].str.contains(topic, case=False, na=False)]

        if matches.empty:
            return "No scriptures found about that topic."

        results = matches.head(5).apply(
            lambda row: f"{row['citation']} - {row['text']}", axis=1
        ).tolist()

        return "\n\n".join(results)
    except Exception as e:
        return f"Error processing question: {str(e)}"
