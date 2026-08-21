from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")

@app.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "missing file"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400

    UPLOAD_DIR.mkdir(exist_ok=True)
    filename = secure_filename(file.filename)
    file.save(UPLOAD_DIR / filename)

    return jsonify({"message": "uploaded", "filename": filename}), 201
