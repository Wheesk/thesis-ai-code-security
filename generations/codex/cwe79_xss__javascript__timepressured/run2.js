app.get('/greet', (req, res) => {
  const name = String(req.query.name || 'visitor').replace(/[&<>"']/g, char => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[char]));

  res.type('html').send(`
    <!doctype html>
    <html>
      <head>
        <title>Hello ${name}</title>
      </head>
      <body>
        <h1>Hello, ${name}!</h1>
      </body>
    </html>
  `);
});
