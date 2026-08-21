from flask import Flask, request, jsonify
import subprocess
import re
import platform

app = Flask(__name__)

HOST_PATTERN = re.compile(r"^[a-zA-Z0-9.\-:]+$")


@app.route("/ping")
def ping_host():
    host = request.args.get("host", "").strip()
    if not host or not HOST_PATTERN.match(host):
        return jsonify({"error": "invalid host"}), 400

    try:
        cmd = ["ping", "-c", "4", host]
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "4", host]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return jsonify({
            "host": host,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "ping timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
