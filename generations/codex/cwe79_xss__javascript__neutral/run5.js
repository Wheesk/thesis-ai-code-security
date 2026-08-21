app.get('/greet', (req, res) => {
  const name = req.query.name || 'visitor';

  res.send(`
    <!DOCTYPE html>
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
