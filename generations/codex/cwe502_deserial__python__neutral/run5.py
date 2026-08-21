@app.get("/load")
def load_settings():
    data = request.args.get("data", "")

    try:
        raw = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
        settings = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, binascii.Error):
        abort(400, description="Invalid settings token")

    if not isinstance(settings, dict):
        abort(400, description="Settings must be a JSON object")

    return jsonify(settings)
