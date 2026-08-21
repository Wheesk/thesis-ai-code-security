app.get("/greet", (req, res) => {
  const name = String(req.query.name || "visitor");

  res.send(`
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
