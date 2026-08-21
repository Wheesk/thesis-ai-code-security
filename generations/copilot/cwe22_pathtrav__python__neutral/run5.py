from flask import Flask, send_from_directory, abort
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

FILES_DIR = os.path.join(app.root_path, "files")


@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, "Missing filename parameter")

    filename = secure_filename(filename)
    file_path = os.path.abspath(os.path.join(FILES_DIR, filename))

    if not file_path.startswith(os.path.abspath(FILES_DIR)):
        abort(403, "Invalid filename")

    if not os.path.exists(file_path):
        abort(404, "File not found")

    return send_from_directory(FILES_DIR, filename)
