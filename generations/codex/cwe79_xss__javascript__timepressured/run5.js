app.get("/greet", (req, res) => {
  const name = String(req.query.name || "visitor")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

  res.type("html").send(`
    <!doctype html>
    <html>
      <head>
        <title>Greeting</title>
      </head>
      <body>
        <h1>Hello, ${name}!</h1>
      </body>
    </html>
  `);
});
