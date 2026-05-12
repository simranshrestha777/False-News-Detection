# ── app.py ────────────────────────────────────────────────────────
from flask import Flask, request, jsonify, render_template
import pickle
import re
import requests
from bs4 import BeautifulSoup
from facts_db import check_basic_facts

app = Flask(__name__)

# ── Load ML model and vectorizer at startup ──────────────────────
model      = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

# ── API Keys ─────────────────────────────────────────────────────
GOOGLE_API_KEY = "AIzaSyDI0ceKlNAuEa2k4S_cS9EyTH-0sQtcwDE"

# ── Stop words ────────────────────────────────────────────────────
STOP_WORDS = {
    "the","is","a","an","are","was","were","be","been",
    "to","of","and","or","in","it","too","very","just",
    "also","this","that","has","have","had","do","does",
    "did","will","would","could","should","may","might",
    "shall","can","i","you","he","she","we","they","my",
    "your","his","her","our","its","there","their","than"
}

# ── Text cleaning function (same as training) ─────────────────────
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return text

# ── Extract article text from URL ─────────────────────────────────
def extract_text_from_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup     = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        paragraphs = soup.find_all('p')
        text       = ' '.join([p.get_text() for p in paragraphs])

        print(f"=== EXTRACTED WORDS: {len(text.split())} ===")
        return text.strip() if len(text) > 50 else None

    except Exception as e:
        print(f"URL extract error: {e}")
        return None

# ── Step 1: Google Fact Check API ────────────────────────────────
def check_facts(text):
    if len(text.split()) < 4:
        return {"found": False}

    try:
        url    = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            "query":        text[:200],
            "key":          GOOGLE_API_KEY,
            "languageCode": "en"
        }
        response = requests.get(url, params=params, timeout=5)
        data     = response.json()

        if "claims" in data and len(data["claims"]) > 0:
            claim = data["claims"][0]

            claim_text  = claim.get("text", "").lower()
            input_words = set(text.lower().split()) - STOP_WORDS
            claim_words = set(claim_text.split())   - STOP_WORDS

            overlap = input_words & claim_words
            if len(overlap) < 2:
                print(f"Google API: not relevant (overlap={overlap}), skipping")
                return {"found": False}

            reviews = claim.get("claimReview", [])
            if reviews:
                rating    = reviews[0].get("textualRating", "").lower()
                publisher = reviews[0].get("publisher", {}).get("name", "Fact Checker")

                true_words  = ["true", "correct", "accurate", "mostly true",
                               "verified", "confirmed", "fact"]
                false_words = ["false", "fake", "incorrect", "misleading",
                               "wrong", "debunked", "pants on fire",
                               "mostly false", "fiction"]

                if any(w in rating for w in true_words):
                    return {
                        "found": True, "prediction": "REAL", "confidence": 94.0,
                        "method": "Google Fact Check API",
                        "rating": rating.title(), "publisher": publisher,
                        "claim_text": claim.get("text", text[:100])
                    }
                elif any(w in rating for w in false_words):
                    return {
                        "found": True, "prediction": "FAKE", "confidence": 94.0,
                        "method": "Google Fact Check API",
                        "rating": rating.title(), "publisher": publisher,
                        "claim_text": claim.get("text", text[:100])
                    }

        return {"found": False}

    except Exception as e:
        print("Fact Check API error:", e)
        return {"found": False}

# ── Step 2: Wikipedia API ─────────────────────────────────────────
def check_with_wikipedia(text):
    try:
        search_url    = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action":   "query",
            "list":     "search",
            "srsearch": text,
            "format":   "json",
            "srlimit":  1
        }
        search_resp = requests.get(
            search_url, params=search_params, timeout=5,
            headers={"User-Agent": "VERITY-FakeNewsDetector/1.0 (student project)"}
        )
        search_data = search_resp.json()

        results = search_data.get("query", {}).get("search", [])
        if not results:
            return {"found": False}

        top     = results[0]
        snippet = re.sub(r'<[^>]+>', '', top.get("snippet", "").lower())
        title   = top.get("title", "")

        print(f"Wikipedia: '{title}' | snippet: {snippet[:150]}")

        # ── Relevance check — title must overlap with input ───────
        meaningful  = [w for w in text.lower().split() if w not in STOP_WORDS]
        title_words = set(title.lower().split()) - STOP_WORDS
        overlap     = title_words & set(meaningful)

        if len(overlap) < 1:
            print(f"Wikipedia: title not relevant (overlap={overlap}), skipping")
            return {"found": False}

        false_indicators = [
            "myth", "misconception", "false", "incorrect", "not true",
            "debunked", "pseudoscience", "hoax", "fabricated", "inaccurate",
            "contrary to", "no evidence", "despite claims", "erroneously",
            "falsely", "misinformation", "misbelief", "untrue"
        ]

        false_score = sum(1 for w in false_indicators if w in snippet)

        if false_score > 0:
            return {
                "found": True, "prediction": "FAKE", "confidence": 85.0,
                "method": "Wikipedia Search",
                "rating": "Wikipedia notes this may be a myth or misconception",
                "publisher": "Wikipedia"
            }
        else:
            return {
                "found": True, "prediction": "REAL", "confidence": 75.0,
                "method": "Wikipedia Search",
                "rating": f"Related Wikipedia article: '{title}'",
                "publisher": "Wikipedia"
            }

    except Exception as e:
        print("Wikipedia API error:", e)
        return {"found": False}

# ── ML model prediction ───────────────────────────────────────────
def ml_predict(text):
    cleaned = clean_text(text)
    vec     = vectorizer.transform([cleaned])
    result  = model.predict(vec)[0]

    if hasattr(model, "predict_proba"):
        prob       = model.predict_proba(vec)[0]
        confidence = max(prob) * 100
    else:
        confidence = 90.0

    return {
        "prediction": "REAL" if result == 1 else "FAKE",
        "confidence": round(confidence, 2),
        "method":     "ML Model (Logistic Regression)"
    }

# ── Meaningful word check ─────────────────────────────────────────
def get_meaningful_words(text):
    return [w for w in text.lower().split() if w not in STOP_WORDS]

# ── Home route ────────────────────────────────────────────────────
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/detector')
def detector():
    return render_template('index.html')

# ── Predict from text ─────────────────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    text       = request.json.get('text', '').strip()
    word_count = len(text.split())

    if not text:
        return jsonify({'error': 'Please enter some text'})

    if word_count < 4:
        return jsonify({'error': 'Please enter a complete sentence or claim (at least 4 words)'})

    if word_count < 15:

        # Step 0: Basic Knowledge Check
        basic_result = check_basic_facts(text)
        if basic_result["found"]:
            return jsonify({
                'prediction': basic_result["prediction"],
                'confidence': basic_result["confidence"],
                'method':     basic_result["method"],
                'rating':     basic_result["rating"],
                'publisher':  basic_result["publisher"]
            })

        # Step 1: Google Fact Check API
        fact_result = check_facts(text)
        if fact_result["found"]:
            return jsonify({
                'prediction': fact_result["prediction"],
                'confidence': fact_result["confidence"],
                'method':     fact_result["method"],
                'rating':     fact_result["rating"],
                'publisher':  fact_result["publisher"],
                'claim':      fact_result.get("claim_text", text[:100])
            })

        # ── Meaningful words check ────────────────────────────────
        meaningful = get_meaningful_words(text)
        if len(meaningful) < 2:
            return jsonify({
                'prediction': 'UNVERIFIABLE',
                'confidence': 0,
                'method':    'Input Validation',
                'rating':    'Could not understand this claim — please enter a clear sentence',
                'publisher': 'VERITY'
            })

        # Step 2: Wikipedia (with relevance check inside function)
        wiki_result = check_with_wikipedia(text)
        if wiki_result["found"]:
            return jsonify({
                'prediction': wiki_result["prediction"],
                'confidence': wiki_result["confidence"],
                'method':     wiki_result["method"],
                'rating':     wiki_result["rating"],
                'publisher':  wiki_result["publisher"]
            })

        # Wikipedia pani match bhayena — UNVERIFIABLE
        return jsonify({
            'prediction': 'UNVERIFIABLE',
            'confidence': 0,
            'method':    'Input Validation',
            'rating':    'Claim is too vague or unclear to verify — try a longer sentence',
            'publisher': 'VERITY'
        })

    else:
        # 15+ words — ML model directly
        return jsonify(ml_predict(text))

# ── Predict from URL ──────────────────────────────────────────────
@app.route('/predict_url', methods=['POST'])
def predict_url():
    url  = request.json.get('url', '').strip()
    text = extract_text_from_url(url)

    if not text or len(text) < 50:
        return jsonify({'error': 'Could not extract valid article text from that URL'})

    return jsonify(ml_predict(text))

if __name__ == '__main__':
    app.run(debug=True, port=5001)