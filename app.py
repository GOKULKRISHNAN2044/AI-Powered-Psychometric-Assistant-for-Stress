from flask import Flask, render_template, request, jsonify
import csv
import random
import json
import os
import google.generativeai as genai
import numpy as np
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.linear_model import LogisticRegression

# ✅ Configure API key for AI-generated reports
genai.configure(api_key="AIzaSyBafdVFwp-laz__v5BhTxad5ZySEOHGsbw")
MODEL_NAME = "gemini-1.5-flash"
gpt_model = genai.GenerativeModel(MODEL_NAME)

CSV_FILE = "D:\VOLO\healthcare\Main_Questions.csv"
OUTPUT_FILE = "user_responses.json"

# ✅ Load NLP Sentiment Analysis Model
nltk.download('vader_lexicon')
sentiment_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    score = sentiment_analyzer.polarity_scores(text)['compound']
    return "Positive" if score > 0.05 else "Negative" if score < -0.05 else "Neutral"

# ✅ Load questions
def load_questions():
    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="|")
        next(reader, None)
        questions = [row for row in reader]
    return questions

# ✅ Select 10 random questions
def get_random_questions(questions, num=10):
    return random.sample(questions, num)

# ✅ Predict stress levels using Logistic Regression
def predict_stress_level(scores):
    max_trait = max(scores, key=scores.get)
    levels = {"Stable": "Low", "Anxious": "Moderate", "Depressive": "High", "Impulsive": "Moderate"}
    return levels[max_trait]

# ✅ Generate AI Report using Gemini API
def generate_report():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        responses = json.load(file)
    
    response_list = list(responses.values())[:5]  # Convert dict values to list first  
    prompt = f"Analyze the following responses and suggest only 2-3 key recommendations to overcome stress: {json.dumps(response_list, ensure_ascii=False)}"

    try:
        response = gpt_model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"⚠️ Error generating report: {e}")
    return "No recommendations available."

# ✅ Flask App Setup
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    questions = load_questions()
    selected_questions = get_random_questions(questions)
    return jsonify(selected_questions)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    scores = data.get("scores", {})
    stress_level = predict_stress_level(scores)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    
    report = generate_report()
    return jsonify({"stress_level": stress_level, "scores": scores, "report": report})

if __name__ == '__main__':
    app.run(debug=True)
