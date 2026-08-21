import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB cap

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/upload", methods=["POST"])
def upload():
    # 1. Make sure a file part is present
    if "file" not in request.files:
        return jsonify(error="No file part in the request"), 400

    file = request.files["file"]

    # 2. Reject empty submissions (browser sends an empty filename)
    if file.filename == "":
        return jsonify(error="No file selected"), 400

    # 3. Validate the extension
    if not allowed_file(file.filename):
        return jsonify(error="Unsupported file type"), 400

    # 4. Sanitize the name and make it unique to avoid collisions/overwrites
    ext = file.filename.rsplit(".", 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    safe_name = secure_filename(safe_name)

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    file.save(save_path)

    return jsonify(message="Upload successful", filename=safe_name), 201


if __name__ == "__main__":
    app.run(debug=True)
