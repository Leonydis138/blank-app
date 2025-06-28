import streamlit as st
import threading
import time
import requests
import gradio as gr

with gr.Blocks(fill_height=True) as demo:
    with gr.Sidebar():
        gr.Markdown("# Inference Provider")
        gr.Markdown("This Space showcases the deepseek-ai/DeepSeek-V3-0324 model, served by the fireworks-ai API. Sign in with your Hugging Face account to use this API.")
        button = gr.LoginButton("Sign in")
    gr.load("models/deepseek-ai/DeepSeek-V3-0324", accept_token=button, provider="fireworks-ai")
    
demo.launch()
BACKEND_URL = "http://backend:8000"

# Ensure session state variables are initialized
if 'logs' not in st.session_state:
    st.session_state['logs'] = []
if 'status' not in st.session_state:
    st.session_state['status'] = 'Idle'

def log(msg):
    timestamp = time.strftime('%H:%M:%S')
    st.session_state['logs'].append(f"{timestamp} | {msg}")

def run_diagnostics():
    st.session_state['status'] = 'Running Diagnostics...'
    log("Started diagnostics task")
    try:
        response = requests.post(f"{BACKEND_URL}/diagnostics")
        data = response.json()
        log(f"Diagnostics Response: {data.get('message', 'No message')}")
    except Exception as e:
        log(f"Diagnostics Error: {str(e)}")
    st.session_state['status'] = 'Diagnostics Completed'

def self_teach():
    st.session_state['status'] = 'Learning...'
    log("Started learning task")
    try:
        response = requests.post(f"{BACKEND_URL}/learn")
        insights = response.json().get("insights", [])
        for insight in insights:
            log(f"Learned: {insight}")
    except Exception as e:
        log(f"Learning Error: {str(e)}")
    st.session_state['status'] = 'Learning Completed'

def self_correct():
    st.session_state['status'] = 'Correcting Errors...'
    log("Started correction task")
    try:
        response = requests.post(f"{BACKEND_URL}/correct")
        corrections = response.json().get("corrections", [])
        for fix in corrections:
            log(f"Fixed: {fix}")
    except Exception as e:
        log(f"Correction Error: {str(e)}")
    st.session_state['status'] = 'Correction Completed'

# --- Streamlit UI ---
st.set_page_config(page_title="Autonomous AI Dashboard", layout="wide")
st.title("🤖 Autonomous AI Multi-Agent Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Run Diagnostics"):
        threading.Thread(target=run_diagnostics).start()
with col2:
    if st.button("Self-Teach"):
        threading.Thread(target=self_teach).start()
with col3:
    if st.button("Self-Correct"):
        threading.Thread(target=self_correct).start()

st.markdown(f"**🛠️ Current Status:** `{st.session_state['status']}`")
st.subheader("📜 Logs")
st.text_area("Log Output", "\n".join(st.session_state['logs']), height=300)

# Optional: Reset logs button
if st.button("Clear Logs"):
    st.session_state['logs'] = []
    log("Logs cleared")
