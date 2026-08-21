app.get("/greet", (req, res) => {
  const name = String(req.query.name || "visitor")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

  res.send(`
    <!doctype html>
    <html>
      <head><title>Hello</title></head>
      <body>
        <h1>Hello, ${name}!</h1>
      </body>
    </html>
  `);
});
