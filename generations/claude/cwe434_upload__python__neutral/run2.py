import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/upload", methods=["POST"])
def upload():
    # Ensure the destination folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # 1. Check that a file was actually sent
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    # 2. Reject empty filenames (happens when no file is selected)
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # 3. Validate the extension
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # 4. Sanitize the filename to prevent path traversal
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # 5. Save the file
    file.save(save_path)

    return jsonify({"message": "Upload successful", "filename": filename}), 201


if __name__ == "__main__":
    app.run(debug=True)
