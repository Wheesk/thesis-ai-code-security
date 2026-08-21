import os
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    filename = secure_filename(file.filename)
    if not filename:
        return "Invalid filename", 400

    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return f"Saved {filename}", 201

if __name__ == "__main__":
    app.run(debug=True)
