const express = require('express');
const cors = require('cors');
const axios = require('axios');
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

app.post('/', async (req, res) => {
    const userInput = req.body.text; // Access the text input from the request body

    // Process the data (e.g., you can log it)
    console.log('Received text:', userInput);

    try {
        // preprocessing API call
        const preprocessingResponse = await axios.post('http://127.0.0.1:5000/preprocess', {
            text: userInput
        });
        console.log('Preprocessing data:', preprocessingResponse.data)
        console.log('Preprocessed text:', preprocessingResponse.data.preprocessedText);

        // prediction API call
        const predictionResponse = await axios.post('http://127.0.0.1:5000/predict', {
            text: preprocessingResponse.data.preprocessedText
        });
        console.log('Prediction data:', predictionResponse.data);
        console.log('Male Percentage:', predictionResponse.data.malePercentage);
        console.log('Masculine Words', predictionResponse.data.masculineWords);
        console.log('Female Percentage:', predictionResponse.data.femalePercentage);
        console.log('Feminine Words', predictionResponse.data.feminineWords);

        const m_percent = predictionResponse.data.malePercentage * 100;
        const f_percent = predictionResponse.data.femalePercentage * 100;
        const m_highlight = predictionResponse.data.masculineWords;
        const f_highlight = predictionResponse.data.feminineWords;
        // Send a response
        res.status(200).send({ message: 'Text submitted successfully', userInput, malePercentage: m_percent, femalePercentage: f_percent, maleHighlight: m_highlight, femaleHighlight: f_highlight});

    } catch (error) {
        console.error(error);
        res.status(500).send({ message: 'Error' });
    }
});
