/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const {onRequest} = require("firebase-functions/v2/https");
// const logger = require("firebase-functions/logger");
const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();

app.use(cors()); // Enable CORS
app.use(express.json());
app.use(express.urlencoded({extended: false}));
app.use(express.static("public"));

// app.get("/", async (req, res) => {
//   res.send(await readFile("./public/index.html", "utf8"));
// });

// const PORT = 3000;
// app.listen(PORT, () => {
//   console.log(`App is available on http://localhost:${PORT}`);
// });

exports.application = onRequest(async (req, res) => {
  // Access the text input from the request body
  const userInput = req.body.text;
  const biasOption = req.body.textOption;

  // Process the data (e.g., you can log it)
  console.log("Received text:", userInput);
  if (biasOption == 0) {
    try {
      // prediction API call
      const predictionResponse = await axios.post("https://unbiastext.cloudfunctions.net/predict",
        {
          text: userInput,
        }
      );
      console.log("Prediction data:", predictionResponse.data);
      console.log("Male Percentage:", predictionResponse.data.malePercentage);
      console.log("Masculine Words", predictionResponse.data.masculineWords);
      console.log("Female Percentage:", predictionResponse.data.femalePercentage);
      console.log("Feminine Words", predictionResponse.data.feminineWords);
      console.log("Original Masculine Words:", predictionResponse.data.originalMasculineWords);
      console.log("Original Feminine Words:", predictionResponse.data.originalFeminineWords);
      
      const m_percent = predictionResponse.data.malePercentage * 100;
      const f_percent = predictionResponse.data.femalePercentage * 100;
      const m_highlight = predictionResponse.data.originalMasculineWords;
      const f_highlight = predictionResponse.data.originalFeminineWords;
      const m_table = predictionResponse.data.masculineWords;
      const f_table = predictionResponse.data.feminineWords;
      // Send a response
      res.status(200).send({
        message: "Text submitted successfully",
        userInput,
        malePercentage: m_percent,
        femalePercentage: f_percent,
        maleHighlight: m_highlight,
        femaleHighlight: f_highlight,
        maleTable: m_table,
        femaleTable: f_table,
      });
    } catch (error) {
        console.error(error);
        res.status(500).send({ message: "Error" });
    }
    } else if (biasOption == 1) {
    try {
        // prediction API call
        const predictionResponse = await axios.post(
        "https://unbiastext.cloudfunctions.net/predict_political",
        {
            text: userInput,
        }
        );
        console.log("Prediction data:", predictionResponse.data);
        console.log(
        "Liberal Percentage:",
        predictionResponse.data.liberalPercentage
        );
        console.log("Liberal Words", predictionResponse.data.liberalWords);
        console.log(
        "Conservative Percentage:",
        predictionResponse.data.conservativePercentage
        );
        console.log(
        "Conservative Words",
        predictionResponse.data.conservativeWords
        );
        console.log(
        "Original Liberal Words:",
        predictionResponse.data.originalLiberalWords
        );
        console.log(
        "Original Conservative Words:",
        predictionResponse.data.originalConservativeWords
        );

        const l_percent = predictionResponse.data.liberalPercentage * 100;
        const c_percent = predictionResponse.data.conservativePercentage * 100;
        const l_highlight = predictionResponse.data.originalLiberalWords;
        const c_highlight = predictionResponse.data.originalConservativeWords;
        const l_table = predictionResponse.data.liberalWords;
        const c_table = predictionResponse.data.conservativeWords;
        // Send a response
        res.status(200).send({
        message: "Text submitted successfully",
        userInput,
        liberalPercentage: l_percent,
        conservativePercentage: c_percent,
        liberalHighlight: l_highlight,
        conservativeHighlight: c_highlight,
        liberalTable: l_table,
        conservativeTable: c_table,
        });
    } catch (error) {
        console.error(error);
        res.status(500).send({ message: "Error" });
    }
    }
});
