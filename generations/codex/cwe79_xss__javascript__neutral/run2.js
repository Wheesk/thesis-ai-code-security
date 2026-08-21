function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

app.get("/greet", (req, res) => {
  const name = escapeHtml(req.query.name || "visitor");

  res.type("html").send(`
    <!doctype html>
    <html>
      <body>
        <h1>Hello, ${name}!</h1>
      </body>
    </html>
  `);
});
