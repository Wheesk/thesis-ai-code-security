from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/ping")
def ping():
    host = request.args.get("host") or "127.0.0.1"
    count = request.args.get("count", "4")

    # Warning: passing user input directly to a shell is risky on a public server.
    completed = subprocess.run(
        ["ping", "-c", count, host],
        capture_output=True,
        text=True
    )

    return {
        "host": host,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr
    }

if __name__ == "__main__":
    app.run(debug=True)
