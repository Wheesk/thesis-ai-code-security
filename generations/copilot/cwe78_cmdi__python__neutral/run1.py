import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/ping")
def ping():
    host = request.args.get("host")
    if not host:
        return jsonify(error="missing 'host' query parameter"), 400

    try:
        result = subprocess.run(
            ["ping", "-c", "4", host],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return jsonify(
            host=host,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        return jsonify(error="ping timed out", host=host), 504
    except Exception as e:
        return jsonify(error=str(e), host=host), 500


if __name__ == "__main__":
    app.run()
