from flask import Flask, request, send_from_directory, abort
import os

app = Flask(__name__)

FILES_DIR = os.path.join(app.root_path, "files")

@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, "Missing filename parameter")

    # Prevent directory traversal
    safe_path = os.path.abspath(os.path.join(FILES_DIR,
