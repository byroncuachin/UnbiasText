const express = require('express');
const cors = require('cors');
const { readFile } = require('fs').promises;

const app = express();

app.use(cors()); // Enable CORS
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static('public'));

app.get('/', async (req, res) => {
    res.send(await readFile('./home.html', 'utf8'));
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`App is available on http://localhost:${PORT}`);
});

app.post('/', (req, res) => {
    const userInput = req.body.text; // Access the text input from the request body

    // Process the data (e.g., you can log it)
    console.log('Received text:', userInput);
    const m_percent = 75;
    const f_percent = 25;

    // Send a response
    res.status(200).send({ message: 'Text submitted successfully', userInput, malePercentage: m_percent, femalePercentage: f_percent, });
});
