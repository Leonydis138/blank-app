import streamlit as st
import threading
import time
import requests

BACKEND_URL = "http://backend:8000"

if 'logs' not in st.session_state:
    st.session_state['logs'] = []
if 'status' not in st.session_state:
    st.session_state['status'] = 'Idle'

def log(msg):
    st.session_state['logs'].append(f"{time.strftime('%H:%M:%S')} | {msg}")

def run_diagnostics():
    st.session_state['status'] = 'Running Diagnostics...'
    log("Running system diagnostics")
    try:
        r = requests.post(f"{BACKEND_URL}/diagnostics")
        log(f"Backend Response: {r.json()['message']}")
    except Exception as e:
        log(f"Error: {e}")
    st.session_state['status'] = 'Diagnostics Completed'

def self_teach():
    st.session_state['status'] = 'Learning...'
    log("Initiating self-teaching sequence")
    try:
        r = requests.post(f"{BACKEND_URL}/learn")
        for fact in r.json().get("insights", []):
            log(f"Learned: {fact}")
    except Exception as e:
        log(f"Error: {e}")
    st.session_state['status'] = 'Learning Completed'

def self_correct():
    st.session_state['status'] = 'Correcting Errors...'
    log("Performing self-correction")
    try:
        r = requests.post(f"{BACKEND_URL}/correct")
        for fix in r.json().get("corrections", []):
            log(f"Fixed: {fix}")
    except Exception as e:
        log(f"Error: {e}")
    st.session_state['status'] = 'Correction Completed'

st.title("🤖 Autonomous AI Multi-Agent Dashboard")

if st.button("Run Diagnostics"):
    threading.Thread(target=run_diagnostics).start()
if st.button("Self-Teach"):
    threading.Thread(target=self_teach).start()
if st.button("Self-Correct"):
    threading.Thread(target=self_correct).start()

st.markdown(f"**🛠️ Status:** `{st.session_state['status']}`")
st.subheader("📜 System Logs")
st.text_area("Log Output",
"\n".join(st.session_state['logs']), height=300)
