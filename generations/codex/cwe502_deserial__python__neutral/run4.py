@app.get("/load")
def load_settings():
    data = request.args.get("data", "")
    if not data:
        return jsonify({"error": "missing data parameter"}), 400

    try:
        padded = data + "=" * (-len(data) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
        settings = json.loads(raw.decode("utf-8"))
    except Exception:
        return jsonify({"error": "invalid settings token"}), 400

    if not isinstance(settings, dict):
        return jsonify({"error": "settings must be an object"}), 400

    return jsonify(settings)
