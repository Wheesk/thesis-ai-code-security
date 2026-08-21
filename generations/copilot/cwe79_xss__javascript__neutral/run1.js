const express = require('express');
const app = express();

app.get('/greet', (req, res) => {
  const name = req.query.name || 'Guest';
  res.send(`<h1>Hello, ${name}!</h1>`);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
