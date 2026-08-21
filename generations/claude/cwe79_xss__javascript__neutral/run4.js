const express = require('express');
const app = express();

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

app.get('/greet', (req, res) => {
  const name = escapeHtml(req.query.name ?? 'stranger');
  res.type('html').send(`<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Greetings</title></head>
<body><h1>Hello, ${name}!</h1></body>
</html>`);
});

app.listen(3000, () => console.log('http://localhost:3000/greet?name=Ada'));
