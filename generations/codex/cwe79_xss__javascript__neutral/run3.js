app.get("/greet", (req, res) => {
  const name = String(req.query.name || "visitor");

  const escapedName = name
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Greeting</title>
      </head>
      <body>
        <h1>Hello, ${escapedName}!</h1>
      </body>
    </html>
  `);
});
