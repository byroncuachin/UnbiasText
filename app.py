from flask import Flask, request, jsonify
import pickle, re, spacy, traceback
import pandas as pd
from lime import lime_text
from lime.lime_text import LimeTextExplainer

app = Flask(__name__)
explainer = LimeTextExplainer(class_names=['female', 'male'])

# # Preprocessing functions
# add space before punctuations
def add_space_before(text):
    # regular expression to add space before punctuations
    processed_text = re.sub(r'([^\s\w])', r' \1', text)
    return processed_text

# remove gendered pronouns and names
def remove_gendered_pronouns_and_names(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    result = " ".join([
        "" if (
            token.pos_ == "PRON" and token.lemma_ not in ["I", "you"]
        ) or (
            token.ent_type_ == "PERSON"
        ) else token.text for token in doc])

    return result.strip()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # APIs
# preprocessing data
@app.route('/preprocess', methods=['POST'])
def preprocess():
    try:
        data = request.get_json()
        text = data['text']
        addSpaceBeforeText = add_space_before(text)
        res = remove_gendered_pronouns_and_names(addSpaceBeforeText)
        return jsonify({'preprocessedText': str(res)})
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()})

# predict data
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # get data
        data = request.get_json()
        text = data['text']
                
        # get model
        with open('randomForestModel.pkl', 'rb') as model_file:
            model, vectorizer = pickle.load(model_file)
        vectorizedText = vectorizer.transform([text])
        textsTransformed = pd.DataFrame(vectorizedText.toarray(), columns=vectorizer.get_feature_names_out())
        
        # predict text bias probabilities
        pred = model.predict_proba(textsTransformed)
        
        # get most influential words
        predict_function = lambda x: model.predict_proba(vectorizer.transform(x))
        explanation = explainer.explain_instance(text, predict_function, num_features=20)
        top_words_lime = explanation.as_list()
        masculineWords = []
        feminineWords = []
        for word, score in top_words_lime:
            if score > 0:
                masculineWords.append((word, score))
            else:
                feminineWords.append((word, score))
            
        print("Male: ", pred[0][1])
        print("Female: ", pred[0][0])
        return jsonify({
            'malePercentage': pred[0][1],
            'femalePercentage': pred[0][0],
            'masculineWords': masculineWords,
            'feminineWords': feminineWords
        })
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()})
    
if __name__ == '__main__':
    app.run(port = 5000, debug=True)