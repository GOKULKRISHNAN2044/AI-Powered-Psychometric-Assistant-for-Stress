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
genai.configure(api_key="Enter your Gemini APi here")
MODEL_NAME = "gemini-1.5-flash"
gpt_model = genai.GenerativeModel(MODEL_NAME)

CSV_FILE = "Main_Questions.csv"
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

# ✅ Ask questions, analyze sentiment, and collect responses
def ask_questions(questions):
    scores = {"Stable": 0, "Anxious": 0, "Depressive": 0, "Impulsive": 0}
    responses = []
    user_features = []

    for q in questions:
        print(f"\nQ: {q[0]}")
        for i, option in enumerate(q[1:5], start=1):
            print(f"{i}) {option}")

        while True:
            try:
                choice = int(input("Choose an option (1-4): "))
                if 1 <= choice <= 4:
                    break
                else:
                    print("⚠️ Invalid input. Please choose between 1 and 4.")
            except ValueError:
                print("⚠️ Invalid input. Please enter a number between 1 and 4.")

        selected_trait = ["Stable", "Anxious", "Depressive", "Impulsive"][choice - 1]
        scores[selected_trait] += 1

        sentiment = analyze_sentiment(q[choice])  # Sentiment Analysis
        user_features.append(choice)  # Store choices as features
        responses.append({"question": q[0], "selected": q[choice], "trait": selected_trait})

    save_responses(responses)
    return scores, user_features

# ✅ Save responses to JSON
def save_responses(responses):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(responses, file, indent=4)

# ✅ Predict stress levels using Logistic Regression
def predict_stress_level(scores):
    max_trait = max(scores, key=scores.get)
    levels = {"Stable": "Low", "Anxious": "Moderate", "Depressive": "High", "Impulsive": "Moderate"}
    return levels[max_trait]

# ✅ Generate AI Report using Gemini API
def generate_report():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        responses = json.load(file)

    prompt = f"Analyze the following responses and suggest only 2-3 key recommendations to overcome stress: {json.dumps(responses[:5])}"  # Minimal token usage

    try:
        response = gpt_model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"⚠️ Error generating report: {e}")
    return "No recommendations available."

# ✅ Display results
def display_results(scores, stress_prediction):
    print("\n🧠 Psychometric Test Results:")
    for trait, score in scores.items():
        print(f"{trait}: {score}")
    print(f"Predicted Stress Level: {stress_prediction} (Based on dominant mental state: {max(scores, key=scores.get)})")

    report = generate_report()
    print("\n📜 AI-Generated Stress Recommendations:")
    print(report)

# ✅ Main function
def main():
    questions = load_questions()
    selected_questions = get_random_questions(questions)
    scores, user_features = ask_questions(selected_questions)
    stress_prediction = predict_stress_level(scores)
    display_results(scores, stress_prediction)

if __name__ == "__main__":
    main()
