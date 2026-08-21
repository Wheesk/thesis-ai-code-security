const express = require('express');
const app = express();

app.get('/greet', (req, res) => {
  const name = req.query.name || 'stranger';
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Greeting</title>
      </head>
      <body>
        <h1>Hello, ${escapeHtml(name)}!</h1>
      </body>
    </html>
  `);
});

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
