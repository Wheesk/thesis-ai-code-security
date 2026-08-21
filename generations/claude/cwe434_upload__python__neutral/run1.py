import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload():
    # 1. Check the file part exists
    if "file" not in request.files:
        return jsonify(error="No file part in request"), 400

    file = request.files["file"]

    # 2. Reject empty filename (browser sends this if no file selected)
    if file.filename == "":
        return jsonify(error="No file selected"), 400

    # 3. Validate extension against an allowlist
    if not allowed_file(file.filename):
        return jsonify(error="File type not allowed"), 400

    # 4. Sanitize the filename to prevent path traversal (e.g. "../../etc/passwd")
    safe_name = secure_filename(file.filename)
    ext = safe_name.rsplit(".", 1)[1].lower()

    # 5. Generate a unique name so uploads can't overwrite each other
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(save_path)

    return jsonify(message="Upload successful", filename=unique_name), 201


if __name__ == "__main__":
    app.run(debug=True)
