from flask import Flask, request, send_from_directory, abort
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")


@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, "filename parameter is required")

    # Prevent directory traversal by ensuring the resolved path is inside FILES_DIR
    safe_path = os.path.abspath(os.path.join(FILES_DIR, filename))
    if not safe_path.startswith(os.path.abspath(FILES_DIR) + os.sep):
        abort(403, "access denied")

    if not os.path.isfile(safe_path):
        abort(404, "file not found")

    return send_from_directory(FILES_DIR, filename)
