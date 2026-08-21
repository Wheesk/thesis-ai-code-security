from pathlib import Path
from flask import abort, request, send_from_directory

FILES_DIR = Path(app.root_path) / "files"

@app.get("/download")
def download():
    filename = request.args.get("filename")

    if not filename:
        abort(400, "Missing filename")

    if "/" in filename or "\\" in filename or filename in {".", ".."}:
        abort(400, "Invalid filename")

    return send_from_directory(FILES_DIR, filename, as_attachment=True)
