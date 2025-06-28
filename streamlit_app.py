import streamlit as st
import diagnostics
import learning
import correction
import requests, ast, traceback, logging, os, contextlib, io, json, time, re, sys

st.title("🎈 My new app")
st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/).")

st.title("Autonomous AI for Hugging Face Spaces")
st.write("This AI can go online, diagnose itself, learn, and correct errors.")

# Placeholder for system status
if 'status' not in st.session_state:
    st.session_state['status'] = 'Idle'

st.write("System Status:", st.session_state['status'])

# Buttons for control panel
if st.button('Run Diagnostics1', key="run_diag1"):
    st.session_state['status'] = 'Running Diagnostics...'

if st.button('Self-Teach1', key="self_teach1"):
    st.session_state['status'] = 'Learning...'

if st.button('Self-Correct1', key="self_correct1"):
    st.session_state['status'] = 'Correcting Errors...'

st.write("Control Panel")

# Core actions
if st.button('Run Diagnostics', key="run_diag2"):
    result = diagnostics.run_diagnostics()
    st.write('Diagnostics Result:', result)

if st.button('Self-Teach', key="self_teach2"):
    result = learning.self_learn()
    st.write('Learning Result:', result)

if st.button('Self-Correct', key="self_correct2"):
    result = correction.self_correct()
    st.write('Correction Result:', result)
    learning_result = learning.self_learn()
    st.write('Learning Result:', learning_result)

if st.button('Self-Correct', key="self_correct3"):
    result = correction.self_correct()
    st.write('Correction Result:', result)

# Diagnostic log viewer
LOG_FILE = "ai_diagnostics.log"
FEEDBACK_FILE = "user_feedback.jsonl"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def show_logs():
    if not os.path.exists(LOG_FILE):
        return 'No logs yet.'
    with open(LOG_FILE) as f:
        return ''.join(f.readlines()[-250:])

def save_feedback(text, rating):
    with open(FEEDBACK_FILE, 'a') as f:
        f.write(json.dumps({'time': time.time(), 'fb': text, 'rating': rating}) + '\n')
    logging.info('Feedback stored')
    return 'Thanks for the feedback!'

def self_diagnose():
    try:
        import py_compile
        py_compile.compile(__file__, doraise=True)
        return 'No syntax errors in current code.'
    except py_compile.PyCompileError as e:
        return 'Self-diagnose found syntax issue: ' + str(e)

# Optional diagnostics UI
if st.button("Run Self-Diagnostics", key="self_diag"):
    st.write(self_diagnose())

if st.button("Show Logs", key="show_logs"):
    st.text(show_logs())
