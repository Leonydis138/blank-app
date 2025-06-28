
import streamlit as st
import os
import json
import logging
from transformers import pipeline
import pandas as pd
from hashlib import sha256

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize the NLP model
nlp = pipeline("text-generation", model="gpt2")

def load_json_data(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f)
    return {}

def save_json_data(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)

# Load user data
user_data = load_json_data("user_data.json")
user_responses = {}
user_feedback = {}
history = []

# Function to create a hashed password
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# User Authentication
def login(username, password):
    if username in user_data and user_data[username]['password'] == hash_password(password):
        return True
    return False

def register(username, password):
    if username not in user_data:
        user_data[username] = {'password': hash_password(password), 'responses': {}, 'feedback': {}}
        save_json_data("user_data.json", user_data)
        return True
    return False

def main():
    st.title("Better AI Version with User Authentication")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Select Action", menu)

    if choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Login"):
            if login(username, password):
                st.success(f"Welcome *{username}*!")
                user_responses = user_data[username]['responses']
                user_feedback = user_data[username]['feedback']
                global history
                history = load_json_data(username + "_history.json")
            else:
                st.error("Invalid username or password")

    if choice == "Register":
        st.subheader("Register Section")
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type='password')

        if st.button("Register"):
            if register(username, password):
                st.success("Registration successful! Please log in.")
            else:
                st.error("Username already exists.")

    # Once user is logged in, show interaction section
    if "Welcome" in st.session_state:
        st.header("AI Interaction")
        user_input = st.text_input("Ask me anything:")

        if st.button("Submit"):
            responses = ai_interaction(user_input)
            for response in responses:
                st.write(f"AI: {response}")
            save_interaction(user_input, responses)

            # Collect user feedback
            feedback = st.radio("Was any of these responses helpful?", ("Yes", "No", "Neutral"), key="feedback")
            if st.button("Submit Feedback"):
                save_user_feedback(user_input, feedback)
                user_feedback[user_input] = feedback
                save_json_data("user_data.json", user_data)
                st.success("Feedback submitted!")

        # Display Interaction History
        st.subheader("Interaction History")
        for entry in history:
            st.write(f"**You:** {entry['input']}")
            st.write(f"**AI:** {entry['response']}")

        # User-Defined Responses
        st.header("Define Your Own Responses")
        keyword = st.text_input("Keyword:")
        user_response = st.text_area("Response:")

        if st.button("Save Response"):
            user_responses[keyword.lower()] = user_response
            user_data[username]['responses'] = user_responses
            save_json_data("user_data.json", user_data)
            st.success(f"Response saved for: {keyword}")

        # Data Export Section
        st.header("Export Data")
        export_data()

if __name__ == "__main__":
    main()
