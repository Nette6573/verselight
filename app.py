from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from biblegpt import (
    get_random_verse,
    search_verse,
    generate_bible_style_verse,
    get_scriptures_about_topic  # ✅ import the new function
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/help")
def help_page():
    return render_template("help.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")


@app.route("/api/random", methods=['GET'])
def random_verse():
    return jsonify({"verse": get_random_verse()})

@app.route("/api/search", methods=['GET'])
def search():
    keyword = request.args.get("q", default="")
    return jsonify({"verse": search_verse(keyword)})

@app.route("/api/generate", methods=['GET'])
def generate():
    topic = request.args.get("q", default="")
    verse = generate_bible_style_verse(topic)
    return jsonify({"verse": verse})

# ✅ NEW: Handle natural language questions like "What does the Bible say about love?"
@app.route("/api/question", methods=['GET'])
def ask_question():
    question = request.args.get("q", default="")
    if not question:
        return jsonify({"verse": "Please ask a question like 'What does the Bible say about peace?'"})
    
    verses = get_scriptures_about_topic(question)
    return jsonify({"verses": verses})  # returning as "verses" to distinguish from single "verse"

@app.route("/api/save", methods=["POST"])
def save():
    data = request.get_json()
    verse = data.get("verse")
    if verse:
        from biblegpt import save_verse  # already defined
        save_verse(verse)
        return jsonify({"message": "Verse saved."}), 200
    return jsonify({"error": "No verse provided."}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(debug=True, port=5000)  # For local testing, use this line
#     # app.run()  # For production, use this line