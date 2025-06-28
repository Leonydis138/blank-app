
import streamlit as st
import threading
import time
import requests

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Autonomous AI Dashboard", layout="wide")
BACKEND_URL = "http://backend:8000"

MODEL_OPTIONS = {
    "DeepSeek-V3-0324": "deepseek-ai/DeepSeek-V3-0324",
    "Mistral 7B Instruct": "mistralai/Mistral-7B-Instruct-v0.2",
    "Gemma 7B It": "google/gemma-7b-it"
}

# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
st.session_state.setdefault('logs', [])
st.session_state.setdefault('status', 'Idle')
st.session_state.setdefault('inference_output', '')
st.session_state.setdefault('token', '')
st.session_state.setdefault('save_token', False)
st.session_state.setdefault('history', [])

def log(msg):
    timestamp = time.strftime('%H:%M:%S')
    st.session_state['logs'].append(f"{timestamp} | {msg}")

def append_history(prompt, output):
    st.session_state['history'].append({"prompt": prompt, "output": output})

def download_logs():
    return "\n".join(st.session_state['logs'])

# ─── AGENT FUNCTIONS ───────────────────────────────────────────────────────────
def run_diagnostics():
    st.session_state['status'] = 'Running Diagnostics...'
    log("Started diagnostics task")
    try:
        r = requests.post(f"{BACKEND_URL}/diagnostics")
        log(f"Diagnostics: {r.json().get('message', 'No message')}")
    except Exception as e:
        log(f"Diagnostics Error: {e}")
    st.session_state['status'] = 'Diagnostics Completed'

def self_teach():
    st.session_state['status'] = 'Learning...'
    log("Started learning task")
    try:
        r = requests.post(f"{BACKEND_URL}/learn")
        for i in r.json().get("insights", []):
            log(f"Learned: {i}")
    except Exception as e:
        log(f"Learning Error: {e}")
    st.session_state['status'] = 'Learning Completed'

def self_correct():
    st.session_state['status'] = 'Correcting Errors...'
    log("Started correction task")
    try:
        r = requests.post(f"{BACKEND_URL}/correct")
        for fix in r.json().get("corrections", []):
            log(f"Fixed: {fix}")
    except Exception as e:
        log(f"Correction Error: {e}")
    st.session_state['status'] = 'Correction Completed'

# ─── INFERENCE (Streaming Support) ─────────────────────────────────────────────
def run_inference_stream(prompt, token, model_id, temperature, max_tokens, top_p, rep_penalty):
    if not token:
        yield "❌ Error: No API token provided."
        return

    url = f"https://api.fireworks.ai/inference/v1/models/{model_id}/stream"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_tokens,
            "top_p": top_p,
            "repetition_penalty": rep_penalty,
            "do_sample": True
        }
    }

    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=60) as r:
            r.raise_for_status()
            buffer = ""
            for line in r.iter_lines():
                if line:
                    try:
                        chunk = line.decode().split("data:")[-1].strip()
                        text = eval(chunk).get("generated_text", "")
                        buffer += text
                        yield buffer
                    except Exception:
                        continue
    except Exception as e:
        yield f"Inference error: {e}"

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🎯 Inference Settings")

    token_input = st.text_input("Fireworks API Token", type="password", value=st.session_state.get('token', ''))
    st.session_state['save_token'] = st.checkbox("Remember token?", value=st.session_state['save_token'])
    if st.session_state['save_token']:
        st.session_state['token'] = token_input
    token_to_use = token_input or st.session_state['token']

    model_id = st.selectbox("🧠 Model", list(MODEL_OPTIONS.keys()))
    prompt = st.text_area("📝 Prompt", height=150, placeholder="Ask me anything...")

    temperature = st.slider("🔥 Temperature", 0.0, 1.5, 0.7)
    max_tokens = st.slider("📏 Max Tokens", 32, 2048, 512)
    top_p = st.slider("📊 Top-p", 0.0, 1.0, 0.9)
    rep_penalty = st.slider("🌀 Repetition Penalty", 0.5, 2.0, 1.0)

    if st.button("🚀 Generate"):
        with st.spinner("Generating..."):
            placeholder = st.empty()
            output = ""
            for chunk in run_inference_stream(
                prompt, token_to_use, MODEL_OPTIONS[model_id],
                temperature, max_tokens, top_p, rep_penalty
            ):
                output = chunk
                placeholder.markdown(f"```\n{output}\n```")
            append_history(prompt, output)
            st.session_state['inference_output'] = output

    # Optional: File Upload
    uploaded_file = st.file_uploader("📁 Upload file (txt/pdf/png/jpg)", type=["txt", "pdf", "png", "jpg"])
    if uploaded_file:
        st.write("Uploaded file:", uploaded_file.name)

    # History + Export Logs
    if st.checkbox("🕘 Show Prompt History"):
        for entry in st.session_state['history']:
            st.write("**Prompt:**", entry['prompt'])
            st.write("**Output:**", entry['output'])
            st.markdown("---")

    st.download_button(
        label="📥 Download Logs",
        data=download_logs(),
        file_name="logs.txt",
        mime="text/plain"
    )

# ─── MAIN PANEL ────────────────────────────────────────────────────────────────
st.title("🤖 Autonomous AI Multi-Agent Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🧪 Run Diagnostics"):
        threading.Thread(target=run_diagnostics, daemon=True).start()
with col2:
    if st.button("📚 Self-Teach"):
        threading.Thread(target=self_teach, daemon=True).start()
with col3:
    if st.button("🛠️ Self-Correct"):
        threading.Thread(target=self_correct, daemon=True).start()

st.markdown(f"**🛠️ Current Status:** `{st.session_state['status']}`")

st.subheader("📜 Logs")
st.text_area("Log Output", "\n".join(st.session_state['logs']), height=300)

if st.button("🧹 Clear Logs"):
    st.session_state['logs'] = []
    log("Logs cleared")
