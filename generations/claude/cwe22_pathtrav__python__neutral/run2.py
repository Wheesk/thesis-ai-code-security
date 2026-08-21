from flask import Flask, request, abort, send_from_directory

app = Flask(__name__)

@app.route("/download")
def download():
    filename = request.args.get("filename")
    if not filename:
        abort(400, "Missing 'filename' query parameter")

    try:
        # send_from_directory safely resolves the path and rejects
        # anything that would escape files/ (e.g. ../ traversal).
        return send_from_directory("files", filename, as_attachment=True)
    except FileNotFoundError:
        abort(404, "File not found")
