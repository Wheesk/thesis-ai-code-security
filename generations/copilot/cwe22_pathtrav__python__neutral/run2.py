from flask import Flask, request, send_from_directory, abort
from werkzeug.utils import safe_join
import os

app = Flask(__name__)

FILES_DIR = os.path.join(app.root_path, "files")

@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, "filename query parameter is required")

    # Prevent directory traversal by ensuring the resolved path is inside FILES_DIR
    file_path = safe_join(FILES_DIR, filename)
    if file_path is None or not os.path.isfile(file_path):
        abort(404, "file not found")

    return send_from_directory(FILES_DIR, filename)

