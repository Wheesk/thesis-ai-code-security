@app.get("/load")
def load_settings():
    return {"error": "Refusing to deserialize Python objects from user input. Use signed base64-encoded JSON instead."}, 400
