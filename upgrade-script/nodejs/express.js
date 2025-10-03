/* express web framework */
// when you require express you forgot to place ( ) try this
const express = require('express')();
const app = express;
const port = 3000;

app.get('/', (req, res) => {
    res.send('Hello Express!!!!!!!')
});

// HTTP POST 요청
app.post('/', function (req, res) {
  res.send('Got a POST request');
});

// HTTP PUT 요청
app.put('/user', function (req, res) {
  res.send('Got a PUT request at /user');
});

// HTTP DELETE 요청
app.delete('/user', function (req, res) {
  res.send('Got a DELETE request at /user');
});

app.listen(port, () => {
    console.log('Example app listening on port 3000!')
});