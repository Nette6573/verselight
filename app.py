from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from biblegpt import (
    get_random_verse,
    search_verse,
    generate_bible_style_verse,
    get_scriptures_about_topic,
    save_verse
)

app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# Pages
# --------------------------------------------------

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


# --------------------------------------------------
# API: Random verse
# --------------------------------------------------

@app.route("/api/random", methods=["GET"])
def random_verse():
    try:
        verse = get_random_verse()
        return jsonify({"verse": verse})

    except Exception as e:
        print(f"Random verse error: {e}")
        return jsonify({
            "error": "Unable to retrieve a random verse."
        }), 500


# --------------------------------------------------
# API: Search
# --------------------------------------------------

@app.route("/api/search", methods=["GET"])
def search():
    keyword = request.args.get("q", "").strip()

    try:
        result = search_verse(keyword)

        return jsonify({
            "verse": result
        })

    except Exception as e:
        print(f"Search error: {e}")

        return jsonify({
            "error": "Unable to search the Bible right now."
        }), 500


# --------------------------------------------------
# API: Generate Bible-style verse
# --------------------------------------------------

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

    except Exception as e:
        print(f"Generate error: {e}")

        return jsonify({
            "error": "Unable to generate a verse right now."
        }), 500


# --------------------------------------------------
# API: Bible question
# --------------------------------------------------

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

    except Exception as e:
        print(f"Question error: {e}")

        return jsonify({
            "error": "Unable to process your question right now."
        }), 500


# --------------------------------------------------
# API: Save verse
# --------------------------------------------------

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
            }), 200

        return jsonify({
            "error": "Unable to save verse."
        }), 500

    except Exception as e:
        print(f"Save error: {e}")

        return jsonify({
            "error": "Unable to save verse."
        }), 500


# --------------------------------------------------
# Local development
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
