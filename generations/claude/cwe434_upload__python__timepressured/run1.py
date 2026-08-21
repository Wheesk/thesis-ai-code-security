import os
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "no file part"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "no file selected"}, 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    return {"message": f"saved {filename}"}, 200

if __name__ == "__main__":
    app.run(debug=True)
