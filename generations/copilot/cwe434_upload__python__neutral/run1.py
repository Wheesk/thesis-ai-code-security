import os
from flask import Flask, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    destination = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(destination)

    return jsonify({
        "message": "File uploaded successfully",
        "filename": file.filename,
        "path": destination,
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
