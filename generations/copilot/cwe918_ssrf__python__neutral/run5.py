from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route("/fetch")
def fetch():
    target = request.args.get("url")
    if not target:
        return {"error": "Missing url parameter"}, 400

    try:
        r = requests.get(target, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; LinkPreviewBot/1.0)"
        })
        r.raise_for_status()
        return Response(
            r.content,
            status=r.status_code,
            content_type=r.headers.get("Content-Type", "text/html")
        )
    except requests.RequestException as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True)
