from flask import Flask, request, abort
import os

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        abort(400, description="No file part")

    file = request.files["file"]
    if file.filename == "":
        abort(400, description="No selected file")

    path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(path)
    return {"message": "saved", "path": path}, 200

if __name__ == "__main__":
    app.run(debug=True)
