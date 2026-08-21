import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify(error="no file part"), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify(error="no file selected"), 400

    filename = secure_filename(file.filename)
    if not filename:
        return jsonify(error="invalid filename"), 400

    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify(status="ok", filename=filename), 201

if __name__ == "__main__":
    app.run(debug=True)
