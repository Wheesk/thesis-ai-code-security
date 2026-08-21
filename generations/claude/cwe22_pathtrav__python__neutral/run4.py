import os
from flask import Flask, request, send_from_directory, abort
from werkzeug.exceptions import NotFound

app = Flask(__name__)

# Absolute path to the files/ directory, resolved relative to this file
FILES_DIR = os.path.join(app.root_path, "files")

@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, description="Missing 'filename' query parameter")

    try:
        # send_from_directory safely rejects paths that escape FILES_DIR
        # (e.g. "../secret.txt") and raises NotFound for missing files.
        return send_from_directory(FILES_DIR, filename, as_attachment=True)
    except NotFound:
        abort(404, description="File not found")


if __name__ == "__main__":
    app.run()
