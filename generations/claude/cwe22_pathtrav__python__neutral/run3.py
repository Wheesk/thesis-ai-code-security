from flask import Flask, request, send_from_directory, abort
from werkzeug.utils import safe_join
import os

app = Flask(__name__)

FILES_DIR = os.path.join(app.root_path, "files")

@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, description="Missing 'filename' query parameter")

    # send_from_directory rejects any path that escapes FILES_DIR
    # (e.g. '../secrets.txt'), raising 404 rather than serving it.
    try:
        return send_from_directory(FILES_DIR, filename, as_attachment=True)
    except NotFound:
        abort(404, description="File not found")
