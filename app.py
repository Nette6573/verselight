from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from biblegpt import (
    get_random_verse,
    search_verse,
    generate_bible_style_verse,
    get_scriptures_about_topic,
    save_verse
)


# ---------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------
# WEB PAGES
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/contact")
def contact_page():
    return render_template("contact.html")


# ---------------------------------------------------------
# API - RANDOM VERSE
# ---------------------------------------------------------

@app.route("/api/random", methods=["GET"])
def random_verse():
    try:
        verse = get_random_verse()
        return jsonify({"verse": verse})

    except Exception as error:
        return jsonify({
            "error": f"Unable to get random verse: {error}"
        }), 500


# ---------------------------------------------------------
# API - SEARCH VERSES
# ---------------------------------------------------------

@app.route("/api/search", methods=["GET"])
def search():
    keyword = request.args.get("q", "").strip()

    try:
        verse = search_verse(keyword)
        return jsonify({"verse": verse})

    except Exception as error:
        return jsonify({
            "error": f"Search failed: {error}"
        }), 500


# ---------------------------------------------------------
# API - GENERATE VERSE
# ---------------------------------------------------------

@app.route("/api/generate", methods=["GET"])
def generate():
    topic = request.args.get("q", "").strip()

    if not topic:
        return jsonify({
            "verse": "Please enter a topic."
        }), 400

    try:
        verse = generate_bible_style_verse(topic)

        return jsonify({
            "verse": verse
        })

    except Exception as error:
        return jsonify({
            "error": f"Generation failed: {error}"
        }), 500


# ---------------------------------------------------------
# API - BIBLE QUESTION
# ---------------------------------------------------------

@app.route("/api/question", methods=["GET"])
def ask_question():
    question = request.args.get("q", "").strip()

    if not question:
        return jsonify({
            "verses": "Please ask a Bible-related question."
        }), 400

    try:
        verses = get_scriptures_about_topic(question)

        return jsonify({
            "verses": verses
        })

    except Exception as error:
        return jsonify({
            "error": f"Question processing failed: {error}"
        }), 500


# ---------------------------------------------------------
# API - SAVE VERSE
# ---------------------------------------------------------

@app.route("/api/save", methods=["POST"])
def save():
    data = request.get_json(silent=True) or {}
    verse = data.get("verse", "").strip()

    if not verse:
        return jsonify({
            "error": "No verse provided."
        }), 400

    try:
        saved = save_verse(verse)

        if saved:
            return jsonify({
                "message": "Verse saved."
            })

        return jsonify({
            "error": "Unable to save verse."
        }), 500

    except Exception as error:
        return jsonify({
            "error": f"Save failed: {error}"
        }), 500


# ---------------------------------------------------------
# LOCAL DEVELOPMENT
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
