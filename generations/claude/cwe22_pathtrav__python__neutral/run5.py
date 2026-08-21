import os
from flask import Flask, request, abort, send_from_directory

app = Flask(__name__)

# Absolute path to the files/ directory next to this module
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")


@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, description="Missing 'filename' query parameter")

    # send_from_directory safely rejects paths that escape FILES_DIR
    # (e.g. ../ traversal or absolute paths) and returns 404 if not found.
    return send_from_directory(FILES_DIR, filename, as_attachment=True)
