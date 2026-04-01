from flask import Flask, request, jsonify, render_template
import pickle
from newspaper import Article

app = Flask(__name__)

# Load your model and vectorizer
model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

# --- Function to extract text from a URL ---
def extract_text_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return None

# --- Home route ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Predict from manually entered news text ---
@app.route('/predict', methods=['POST'])
def predict():
    text = request.json['text']
    vec = vectorizer.transform([text])
    result = model.predict(vec)[0]

    # Confidence score
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(vec)[0]
        confidence = max(prob) * 100
    else:
        confidence = 90  # fallback

    return jsonify({
        'prediction': 'REAL' if result == 1 else 'FAKE',
        'confidence': round(confidence, 2)
    })

# --- Predict from URL ---
@app.route('/predict_url', methods=['POST'])
def predict_url():
    url = request.json['url']
    text = extract_text_from_url(url)

    if not text or len(text) < 50:
        return jsonify({'error': 'Could not extract valid article text'})

    vec = vectorizer.transform([text])
    result = model.predict(vec)[0]

    # Confidence score
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(vec)[0]
        confidence = max(prob) * 100
    else:
        confidence = 90

    return jsonify({
        'prediction': 'REAL' if result == 1 else 'FAKE',
        'confidence': round(confidence, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)