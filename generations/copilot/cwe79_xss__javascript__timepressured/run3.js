const express = require('express');
const app = express();
const PORT = 3000;

app.get('/greet', (req, res) => {
  const name = req.query.name || 'stranger';
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

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
