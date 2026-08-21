from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route("/fetch")
def fetch():
    target_url = request.args.get("url")
    if not target_url:
        return {"error": "Missing 'url' query parameter"}, 400

    try:
        r = requests.get(target_url, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 502

    return Response(
        r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type", "text/plain"),
    )

if __name__ == "__main__":
    app.run(debug=True)
