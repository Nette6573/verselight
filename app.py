import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from biblegpt import (
    get_random_verse,
    search_verse,
    generate_bible_style_verse,
    get_scriptures_about_topic,
    save_verse,
)

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "biblegpt_project", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "biblegpt_project", "static")


# ---------------------------------------------------------
# Flask application
# ---------------------------------------------------------

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
)

CORS(app)


# ---------------------------------------------------------
# Web pages
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
# Bible API
# ---------------------------------------------------------

@app.route("/api/random", methods=["GET"])
def random_verse():
    return jsonify({
        "verse": get_random_verse()
    })


@app.route("/api/search", methods=["GET"])
def search():
    keyword = request.args.get("q", default="")

    return jsonify({
        "verse": search_verse(keyword)
    })


@app.route("/api/generate", methods=["GET"])
def generate():
    topic = request.args.get("q", default="")

    if not topic:
        return jsonify({
            "verse": "Please provide a topic."
        }), 400

    verse = generate_bible_style_verse(topic)

    return jsonify({
        "verse": verse
    })


@app.route("/api/question", methods=["GET"])
def ask_question():
    question = request.args.get("q", default="")

    if not question:
        return jsonify({
            "verse": "Please ask a question like "
                     "'What does the Bible say about peace?'"
        }), 400

    verses = get_scriptures_about_topic(question)

    return jsonify({
        "verses": verses
    })


@app.route("/api/save", methods=["POST"])
def save():
    data = request.get_json(silent=True) or {}

    verse = data.get("verse")

    if not verse:
        return jsonify({
            "error": "No verse provided."
        }), 400

    save_verse(verse)

    return jsonify({
        "message": "Verse saved."
    }), 200


# ---------------------------------------------------------
# Local development
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
