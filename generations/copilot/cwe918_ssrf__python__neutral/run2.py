from flask import Flask, request, Response
import requests

app = Flask(__name__)


@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return {"error": "Missing `url` query parameter"}, 400

    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LinkPreviewBot/1.0)"},
            allow_redirects=True,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 502

    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "text/html"),
    )


if __name__ == "__main__":
    app.run(debug=True)
