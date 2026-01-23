# APP ARCHITECTURE:  Services  →  Orchestration  →  API Layer  →  UI
import os
import sys
# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename   # Sanitizes uploaded filenames for safety if saving

from worker import process_stt, process_ai_response
from utils.logger import get_logger
import utils.memory as memory

logger = get_logger("SERVER")

# Clear chat history on startup (Session Reset)
memory.clear_history()

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

# -------------------------------------------------
# UI Route
# -------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# -------------------------------------------------
# Voice APIs (2-Step)
# -------------------------------------------------
@app.route("/api/stt", methods=["POST"])
def stt_endpoint():
    """Step 1: Voice -> Text."""
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file"}), 400
        
        audio_file = request.files["audio"]
        audio_bytes = audio_file.read()
        
        result = process_stt(audio_bytes)
        return jsonify(result), 200
    except Exception as e:
        logger.exception("STT endpoint failed")
        return jsonify({"error": "Speech recognition failed"}), 500

@app.route("/api/ai_response", methods=["POST"])
def ai_response_endpoint():
    """Step 2: Text -> LLM -> TTS."""
    try:
        user_text = request.form.get("text")
        voice = request.form.get("voice", "Rachel")
        session_id = request.form.get("session_id", "default")
        
        if not user_text:
            return jsonify({"error": "No text provided"}), 400
            
        result = process_ai_response(user_text, voice, session_id)
        return jsonify(result), 200
    except Exception as e:
        logger.exception("AI endpoint failed")
        return jsonify({"error": "AI response failed"}), 500

# -------------------------------------------------
# Local dev entrypoint
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
