const express = require('express');
const app = express();

app.get('/greet', (req, res) => {
  const name = req.query.name || 'stranger';
  res.send(`<!DOCTYPE html>
<html>
<head><title>Greeting</title></head>
<body>
  <h1>Hello, ${name}!</h1>
</body>
</html>`);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
