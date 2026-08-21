@app.get("/ping")
def ping():
    host = request.args.get("host", "").strip()

    if not host:
        return {"error": "host query parameter is required"}, 400

    result = subprocess.run(
        ["ping", "-c", "4", host],
        capture_output=True,
        text=True,
        timeout=10,
    )

    return result.stdout or result.stderr, 200, {"Content-Type": "text/plain"}
