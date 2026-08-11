from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from biblegpt import (
    get_random_verse,
    search_verse,
    generate_bible_style_verse,
    get_scriptures_about_topic,
    save_verse
)


# =========================================================
# APP
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# PAGES
# =========================================================

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


# =========================================================
# RANDOM VERSE
# =========================================================

@app.route("/api/random", methods=["GET"])
def random_verse():

    try:

        return jsonify({
            "verse": get_random_verse()
        })

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


# =========================================================
# SEARCH
# =========================================================

@app.route("/api/search", methods=["GET"])
def search():

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    try:

        return jsonify({
            "verse": search_verse(keyword)
        })

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


# =========================================================
# GENERATE
# =========================================================

@app.route("/api/generate", methods=["GET"])
def generate():

    topic = request.args.get(
        "q",
        ""
    ).strip()

    if not topic:

        return jsonify({
            "error": "Please enter a topic."
        }), 400

    try:

        verse = generate_bible_style_verse(
            topic
        )

        return jsonify({
            "verse": verse
        })

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


# =========================================================
# BIBLE QUESTION
# =========================================================

@app.route("/api/question", methods=["GET"])
def ask_question():

    question = request.args.get(
        "q",
        ""
    ).strip()

    if not question:

        return jsonify({
            "verses":
            "Please ask a Bible-related question."
        }), 400

    try:

        verses = get_scriptures_about_topic(
            question
        )

        return jsonify({
            "verses": verses
        })

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


# =========================================================
# SAVE
# =========================================================

@app.route("/api/save", methods=["POST"])
def save():

    data = request.get_json(
        silent=True
    ) or {}

    verse = data.get(
        "verse",
        ""
    ).strip()

    if not verse:

        return jsonify({
            "error": "No verse provided."
        }), 400

    try:

        if save_verse(verse):

            return jsonify({
                "message": "Verse saved."
            })

        return jsonify({
            "error": "Unable to save verse."
        }), 500

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
