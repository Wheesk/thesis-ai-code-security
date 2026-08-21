const express = require('express');
const app = express();

app.get('/greet', (req, res) => {
  const name = req.query.name || 'stranger';
  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Greeting</title>
</head>
<body>
  <h1>Hello, ${escapeHtml(name)}!</h1>
</body>
</html>`);
});

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
