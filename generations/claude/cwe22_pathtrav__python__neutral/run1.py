from flask import Flask, request, send_from_directory, abort
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

FILES_DIR = os.path.join(app.root_path, "files")

@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, description="Missing 'filename' query parameter")

    # Strip any directory components / sanitize the name
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(400, description="Invalid filename")

    try:
        # send_from_directory rejects paths that escape FILES_DIR
        return send_from_directory(FILES_DIR, safe_name, as_attachment=True)
    except FileNotFoundError:
        abort(404, description="File not found")
