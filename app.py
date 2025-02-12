import os
import json
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)

# Sample course data
courses = [
    {"name": "Introduction to Python", "provider": "Coursera", "description": "Learn the basics of Python programming."},
    {"name": "Data Science with R", "provider": "edX", "description": "An introduction to data science using R."},
    {"name": "Web Development Bootcamp", "provider": "Udemy", "description": "Become a full-stack web developer."},
    {"name": "Machine Learning", "provider": "Coursera", "description": "Learn machine learning algorithms and techniques."},
    {"name": "Digital Marketing", "provider": "LinkedIn Learning", "description": "Understand the fundamentals of digital marketing."}
]

# Define AI model for course recommendation
vectorizer = TfidfVectorizer()
course_vectors = vectorizer.fit_transform([course['description'] for course in courses])

# Set up Google API credentials
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
SERVICE_ACCOUNT_FILE = 'path/to/service_account_key.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Set up YouTube API client
youtube = build('youtube', 'v3', credentials=credentials)

# Set up Dialogflow API client
import dialogflow
from google.oauth2 import service_account

DIALOGFLOW_PROJECT_ID = 'your-dialogflow-project-id'
DIALOGFLOW_CREDENTIALS = service_account.Credentials.from_service_account_file(
    'path/to/service_account_key.json')

session_client = dialogflow.SessionsClient(credentials=DIALOGFLOW_CREDENTIALS)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_query = request.get_json()['query']
    # Preprocess user query
    user_query = user_query.lower()
    user_query = user_query.replace(',', '').replace('.', '')

    # Use Dialogflow to detect intent
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, 'your-session-id')
    text_input = dialogflow.types.TextInput(text=user_query, language_code='en-US')
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session, query_input)

    # Get intent and entities
    intent = response.query_result.intent.display_name
    entities = response.query_result.parameters

    # Use intent and entities to generate response
    if intent == 'course_recommendation':
        # Calculate similarity between user query and course descriptions
        similarities = cosine_similarity(vectorizer.transform([user_query]), course_vectors)

        # Get top 3 similar courses
        top_courses = sorted(zip(similarities[0], courses), reverse=True)[:3]

        # Generate response
        response_text = 'Based on your query, I recommend the following courses: '
        for course in top_courses:
            response_text += f"{course[1]['name']} ({course[1]['provider']}) - {course[1]['description']}\n"

        # Use YouTube API to get video links
        video_links = []
        for course in top_courses:
            search_response = youtube.search().list(
                q=course[1]['name'],
                part='id,snippet',
                maxResults=1
            ).execute()
            if search_response['items']:
                video_id = search_response['items'][0]['id']['videoId']
                video_link = f"https://www.youtube.com/watch?v={video_id}"
                video_links.append(video_link)

        # Add video links to response
        response_text += '\nHere are some video links to get you started: '
        for link in video_links:
            response_text += f"{link}\n"

        return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)
