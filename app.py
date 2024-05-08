from flask import Flask, request, jsonify
import pickle, re, spacy, traceback
import numpy as np
import pandas as pd
import spacy
from lime import lime_text
from lime.lime_text import LimeTextExplainer
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer

app = Flask(__name__)
stemmer = PorterStemmer()


# # Preprocessing functions
# add space before punctuations
def add_space_before(text):
    # regular expression to add space before punctuations
    processed_text = re.sub(r"([^\s\w])", r" \1", text)
    return processed_text


# remove gendered pronounds, names, stop words, and apply stemming
nlp = spacy.load("en_core_web_sm")
def removeUnnecessaryWords(text):
    doc = nlp(text)

    result = " ".join(
        [
            (
                ""
                if (token.pos_ == "PRON" and token.lemma_ not in ["I", "you"])
                or (
                    token.ent_type_ == "PERSON"
                    or token.text.lower()
                    in ["woman", "women", "man", "men", "he", "she", "him", "her"]
                )
                or (token.text.lower() in STOP_WORDS)
                else stemmer.stem(token.lemma_)
            )
            for token in doc
        ]
    )

    return result.strip()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# # APIs
# predict data
@app.route("/predict", methods=["POST"])
def predict():
    try:
        explainer = LimeTextExplainer(class_names=["female", "male"])
        # get data
        data = request.get_json()
        # text = data["text"]
        text = data.get("text")
        # biasType = data.get("textOption")
        originalText = text

        # if biasType == 0:  # Gender
        # preprocessing text
        addSpaceBeforeText = add_space_before(text)
        text = removeUnnecessaryWords(addSpaceBeforeText)
        print("Text after preprocessing: ", text)

        # get model with vectorizer
        # with open("savedModels/svmModel.pkl", "rb") as model_file:
        with open("savedModels/randomForestModel.pkl", "rb") as model_file:
            model, vectorizer = pickle.load(model_file)
        vectorizedText = vectorizer.transform([text])
        textsTransformed = pd.DataFrame(
            vectorizedText.toarray(), columns=vectorizer.get_feature_names_out()
        )
        # predict text bias probabilities
        pred = model.predict_proba(textsTransformed)
        # get most influential words
        predict_function = lambda x: model.predict_proba(vectorizer.transform(x))

        # # get model using word spacy word embeddings (doesn't work)
        # nlp = spacy.load("en_core_web_md")
        # def text_to_vectors(text):
        #     doc = nlp(text)
        #     return doc.vector
        # with open('savedModels/randomForestModelSpacyEmbeddings.pkl', 'rb') as model_file:
        #     model = pickle.load(model_file)
        # transformedText = np.array([text_to_vectors(t) for t in text])
        # # predict text bias probabilities
        # predict_function = lambda x: model.predict_proba(np.array([text_to_vectors(t) for t in x]))
        # pred = model.predict(transformedText)

        explanation = explainer.explain_instance(
            text, predict_function, num_features=100
        )
        top_words_lime = explanation.as_list()

        masculineWords = []
        feminineWords = []
        for word, score in top_words_lime:
            if score > 0:
                masculineWords.append((word, round(score, 3)))
            else:
                feminineWords.append((word, round(score, 3)))

        # make the amount of masculine and feminine words equal
        masculineWords = masculineWords[:10]
        feminineWords = feminineWords[:10]
        if len(masculineWords) != len(feminineWords):
            masculineWords = masculineWords[
                : min(len(masculineWords), len(feminineWords))
            ]
            feminineWords = feminineWords[
                : min(len(masculineWords), len(feminineWords))
            ]

        # get original words from stemmed words (map)
        masculineStemmedWords = [stemmer.stem(word) for word, score in masculineWords]
        feminineStemmedWords = [stemmer.stem(word) for word, score in feminineWords]
        originalMasculineWords = []
        originalFeminineWords = []
        for stemmedWord in masculineStemmedWords:
            for token in originalText.split():
                if stemmer.stem(token) == stemmedWord:
                    originalMasculineWords.append(token)
                    break
        for stemmedWord in feminineStemmedWords:
            for token in originalText.split():
                if stemmer.stem(token) == stemmedWord:
                    originalFeminineWords.append(token)
                    break

        print("Male Percentage: ", pred[0][1])
        print("Female Percentage: ", pred[0][0])
        print("Masculine Words: ", masculineWords)
        print("Feminine Words: ", feminineWords)
        print("Original Masculine Words: ", originalMasculineWords)
        print("Original Feminine Words: ", originalFeminineWords)
        return jsonify(
            {
                "malePercentage": round(pred[0][1], 2),
                "femalePercentage": round(pred[0][0], 2),
                "masculineWords": masculineWords,
                "feminineWords": feminineWords,
                "originalMasculineWords": originalMasculineWords,
                "originalFeminineWords": originalFeminineWords,
            }
        )
        # elif biasType == 1:  # Political
        #     # preprocessing text
        #     text = add_space_before(text)
        #     print("Text after preprocessing: ", text)

        #     # get model with vectorizer
        #     # with open("savedModels/svmModel.pkl", "rb") as model_file:
        #     with open("savedModels/politicalCCModel.pkl", "rb") as model_file:
        #         model, vectorizer = pickle.load(model_file)
        #     vectorizedText = vectorizer.transform([text])
        #     textsTransformed = pd.DataFrame(
        #         vectorizedText.toarray(), columns=vectorizer.get_feature_names_out()
        #     )
        #     # predict text bias probabilities
        #     pred = model.predict_proba(textsTransformed)
        #     # get most influential words
        #     predict_function = lambda x: model.predict_proba(vectorizer.transform(x))

        #     explanation = explainer.explain_instance(
        #         text, predict_function, num_features=100
        #     )
        #     top_words_lime = explanation.as_list()

        #     liberalWords = []
        #     conservativeWords = []
        #     for word, score in top_words_lime:
        #         if score > 0:
        #             liberalWords.append((word, round(score, 3)))
        #         else:
        #             conservativeWords.append((word, round(score, 3)))

        #     # make the amount of liberal and conservative words equal
        #     liberalWords = liberalWords[:10]
        #     conservativeWords = conservativeWords[:10]
        #     if len(liberalWords) != len(conservativeWords):
        #         liberalWords = liberalWords[
        #             : min(len(liberalWords), len(conservativeWords))
        #         ]
        #         conservativeWords = conservativeWords[
        #             : min(len(liberalWords), len(conservativeWords))
        #         ]

        #     # get original words from stemmed words (map)
        #     liberalStemmedWords = [stemmer.stem(word) for word, score in liberalWords]
        #     conservativeStemmedWords = [
        #         stemmer.stem(word) for word, score in conservativeWords
        #     ]
        #     originalLiberalWords = []
        #     originalConservativeWords = []
        #     for stemmedWord in liberalStemmedWords:
        #         for token in originalText.split():
        #             if stemmer.stem(token) == stemmedWord:
        #                 originalLiberalWords.append(token)
        #                 break
        #     for stemmedWord in conservativeStemmedWords:
        #         for token in originalText.split():
        #             if stemmer.stem(token) == stemmedWord:
        #                 originalConservativeWords.append(token)
        #                 break

        #     print("Liberal Percentage: ", pred[0][1])
        #     print("Conservative Percentage: ", pred[0][0])
        #     print("Liberal Words: ", liberalWords)
        #     print("Conservative Words: ", conservativeWords)
        #     print("Original Liberal Words: ", originalLiberalWords)
        #     print("Original Conservative Words: ", originalConservativeWords)
        #     return jsonify(
        #         {
        #             "liberalPercentage": round(pred[0][1], 2),
        #             "conservativePercentage": round(pred[0][0], 2),
        #             "liberalWords": liberalWords,
        #             "conservativeWords": conservativeWords,
        #             "originalLiberalWords": originalLiberalWords,
        #             "originalConservativeWords": originalConservativeWords,
        #         }
        #     )
        # else:
        #     return jsonify(
        #         {
        #             "malePercentage": biasType,
        #             "femalePercentage": 0,
        #             "masculineWords": [],
        #             "feminineWords": [],
        #             "originalMasculineWords": [],
        #             "originalFeminineWords": [],
        #         }
        #     )  # redundant case
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()})


@app.route("/predictPolitical", methods=["POST"])
def predict_political():
    try:
        explainer = LimeTextExplainer(class_names=["conservative", "liberal"])
        # get data
        data = request.get_json()
        # text = data["text"]
        text = data.get("text")
        # biasType = data.get("textOption")
        originalText = text
        # preprocessing text
        # text = add_space_before(text)
        # print("Text after preprocessing: ", text)
        addSpaceBeforeText = add_space_before(text)
        text = removeUnnecessaryWords(addSpaceBeforeText)
        print("Text after preprocessing: ", text)

        # get model with vectorizer
        # with open("savedModels/svmModel.pkl", "rb") as model_file:
        with open("savedModels/politicalCCModel.pkl", "rb") as model_file:
            model, vectorizer = pickle.load(model_file)
        vectorizedText = vectorizer.transform([text])
        textsTransformed = pd.DataFrame(
            vectorizedText.toarray(), columns=vectorizer.get_feature_names_out()
        )
        # predict text bias probabilities
        pred = model.predict_proba(textsTransformed)
        # get most influential words
        predict_function = lambda x: model.predict_proba(vectorizer.transform(x))

        explanation = explainer.explain_instance(
            text, predict_function, num_features=100
        )
        top_words_lime = explanation.as_list()

        liberalWords = []
        conservativeWords = []
        for word, score in top_words_lime:
            if score > 0:
                liberalWords.append((word, round(score, 3)))
            else:
                conservativeWords.append((word, round(score, 3)))

        # make the amount of liberal and conservative words equal
        liberalWords = liberalWords[:10]
        conservativeWords = conservativeWords[:10]
        if len(liberalWords) != len(conservativeWords):
            liberalWords = liberalWords[
                : min(len(liberalWords), len(conservativeWords))
            ]
            conservativeWords = conservativeWords[
                : min(len(liberalWords), len(conservativeWords))
            ]

        # get original words from stemmed words (map)
        liberalStemmedWords = [stemmer.stem(word) for word, score in liberalWords]
        conservativeStemmedWords = [
            stemmer.stem(word) for word, score in conservativeWords
        ]
        originalLiberalWords = []
        originalConservativeWords = []
        for stemmedWord in liberalStemmedWords:
            for token in originalText.split():
                if stemmer.stem(token) == stemmedWord:
                    originalLiberalWords.append(token)
                    break
        for stemmedWord in conservativeStemmedWords:
            for token in originalText.split():
                if stemmer.stem(token) == stemmedWord:
                    originalConservativeWords.append(token)
                    break

        print("Liberal Percentage: ", pred[0][1])
        print("Conservative Percentage: ", pred[0][0])
        print("Liberal Words: ", liberalWords)
        print("Conservative Words: ", conservativeWords)
        print("Original Liberal Words: ", originalLiberalWords)
        print("Original Conservative Words: ", originalConservativeWords)
        return jsonify(
            {
                "liberalPercentage": round(pred[0][1], 2),
                "conservativePercentage": round(pred[0][0], 2),
                "liberalWords": liberalWords,
                "conservativeWords": conservativeWords,
                "originalLiberalWords": originalLiberalWords,
                "originalConservativeWords": originalConservativeWords,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
