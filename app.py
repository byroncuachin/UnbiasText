from flask import Flask, request, jsonify
import pickle, re, spacy, traceback
import pandas as pd
import spacy
from lime import lime_text
from lime.lime_text import LimeTextExplainer
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer

app = Flask(__name__)
explainer = LimeTextExplainer(class_names=['female', 'male'])
stemmer = PorterStemmer()

# # Preprocessing functions
# add space before punctuations
def add_space_before(text):
    # regular expression to add space before punctuations
    processed_text = re.sub(r'([^\s\w])', r' \1', text)
    return processed_text

# remove gendered pronounds, names, stop words, and apply stemming
def removeUnnecessaryWords(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    result = " ".join([
        "" if (
            token.pos_ == "PRON" and token.lemma_ not in ["I", "you"]
        ) or (
            token.ent_type_ == "PERSON" or token.text.lower() in ["woman", "women", "man", "men", "he", "she", "him", "her"]
        ) or (
            token.text.lower() in STOP_WORDS
        ) else stemmer.stem(token.lemma_) for token in doc])

    return result.strip()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # APIs
# predict data
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # get data
        data = request.get_json()
        text = data['text']
        originalText = text
        
        # preprocessing text
        addSpaceBeforeText = add_space_before(text)
        text = removeUnnecessaryWords(addSpaceBeforeText)
                
        # get model
        with open('savedModels/randomForestModel.pkl', 'rb') as model_file:
            model, vectorizer = pickle.load(model_file)
        vectorizedText = vectorizer.transform([text])
        textsTransformed = pd.DataFrame(vectorizedText.toarray(), columns=vectorizer.get_feature_names_out())
        
        # predict text bias probabilities
        pred = model.predict_proba(textsTransformed)
                
        # get most influential words
        predict_function = lambda x: model.predict_proba(vectorizer.transform(x))
        explanation = explainer.explain_instance(text, predict_function, num_features=100)
        top_words_lime = explanation.as_list()
        
        masculineWords = []
        feminineWords = []
        for word, score in top_words_lime:
            if score > 0:
                masculineWords.append((word, round(score, 3)))
            else:
                feminineWords.append((word, round(score, 3)))

        masculineWords = masculineWords[:10]
        feminineWords = feminineWords[:10]
        
        if len(masculineWords) != len(feminineWords):
            masculineWords = masculineWords[:min(len(masculineWords), len(feminineWords))]
            feminineWords = feminineWords[:min(len(masculineWords), len(feminineWords))]
            
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
        return jsonify({
            'malePercentage': round(pred[0][1], 2),
            'femalePercentage': round(pred[0][0], 2),
            'masculineWords': masculineWords,
            'feminineWords': feminineWords,
            'originalMasculineWords': originalMasculineWords,
            'originalFeminineWords': originalFeminineWords
        })
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()})
    
if __name__ == '__main__':
    app.run(port = 5000, debug=True)