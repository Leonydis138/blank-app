import streamlit as st
import threading
import time
import queue
import random
import json
from datetime import datetime
from transformers import pipeline

# ========== THREAD-SAFE LOGGING ==========
log_queue = queue.Queue()

def log(message: str):
    timestamp = time.strftime("%H:%M:%S")
    log_queue.put(f"{timestamp} | {message}")

def remember(task, summary):
    timestamp = datetime.now().isoformat(timespec='seconds')
    st.session_state['memory'].append({
        "task": task,
        "summary": summary,
        "timestamp": timestamp
    })

# ========== LOAD FREE MODEL PIPELINE ==========
@st.cache_resource
def get_text_generator(model_name: str = "distilgpt2"):
    return pipeline("text-generation", model=model_name, device=-1)

text_generator = get_text_generator()

# ========== TASK FUNCTIONS ==========
def run_diagnostics():
    log("🔍 Starting system diagnostics...")
    time.sleep(1)
    report = []
    components = ["CPU", "GPU", "RAM", "Disk", "Network"]
    for comp in components:
        result = random.choice(["OK", "Warning", "Fault"])
        report.append((comp, result))
        log(f"{comp} Check: {result}")
        time.sleep(0.6)
    summary = ", ".join([f"{c}: {r}" for c, r in report])
    remember("Run Diagnostics", f"Diagnostics complete - {summary}")

def self_teach():
    knowledge_sources = ["StackOverflow", "AI Papers", "GitHub", "Docs"]
    log("📘 Starting self-teaching...")
    for source in knowledge_sources:
        log(f"📖 Learning from: {source}")
        time.sleep(1)
    new_abilities = random.choice([
        "Optimized parsing logic", 
        "Improved reasoning patterns", 
        "Faster comprehension",
        "Refactored neural pathways"
    ])
    log(f"🧠 Integrated: {new_abilities}")
    remember("Self-Teach", f"Learned from sources: {', '.join(knowledge_sources)}; integrated {new_abilities}")

def self_correct():
    bugs = ["Memory leak", "Off-by-one error", "Null reference"]
    log("🛠️ Self-correction started...")
    found = random.sample(bugs, k=2)
    for bug in found:
        log(f"🔍 Found issue: {bug}")
        time.sleep(1)
        log(f"✅ Patched: {bug}")
    remember("Self-Correct", f"Resolved: {', '.join(found)}")

def self_improve():
    upgrades = [
        "12% latency improvement", 
        "Enhanced logic pipeline", 
        "New abstraction layer",
        "Reinforced self-monitoring"
    ]
    log("🚀 Initiating self-improvement...")
    time.sleep(1)
    for u in upgrades:
        log(f"✅ {u}")
        time.sleep(0.6)
    remember("Self-Improve", f"Upgrades applied: {', '.join(upgrades)}")

# ========== STREAMLIT UI INIT ==========
st.set_page_config(page_title="Autonomous AI Control", layout="wide")
st.title("🤖 Autonomous AI Control Panel with Real Models")

# Init session state
if "logs" not in st.session_state:
    st.session_state["logs"] = []
if "memory" not in st.session_state:
    st.session_state["memory"] = []
if "task_counts" not in st.session_state:
    st.session_state["task_counts"] = {
        "Run Diagnostics": 0,
        "Self-Teach": 0,
        "Self-Correct": 0,
        "Self-Improve": 0
    }

# Flush queued logs
while not log_queue.empty():
    st.session_state["logs"].append(log_queue.get())

# ========== LLM INTERACTION PANEL ==========
st.subheader("📝 LLM Text Generation")
prompt = st.text_area("Enter a prompt for the text generator:", height=100)
model_option = st.selectbox("Select Model:", ["distilgpt2", "gpt2"])
if st.button("Generate Text"):
    # reload pipeline if model changed
    text_generator = get_text_generator(model_option)
    with st.spinner("Generating..."):
        outputs = text_generator(prompt, max_length=100, num_return_sequences=1)
    generated = outputs[0]['generated_text']
    st.text_area("Generated Text", generated, height=200)
    log(f"Generated text with {model_option}")
    remember("Text Generation", f"Used {model_option} for prompt: '{prompt[:30]}...' ")
    st.session_state["task_counts"]["Text Generation"] = st.session_state.get("task_counts", {}).get("Text Generation", 0) + 1

# ========== TASK TRIGGERS ==========
col1, col2, col3, col4 = st.columns(4)
def run_task(task_fn, label):
    threading.Thread(target=task_fn, daemon=True).start()
    st.session_state["task_counts"][label] += 1

with col1:
    if st.button("🧪 Run Diagnostics"):
        run_task(run_diagnostics, "Run Diagnostics")
with col2:
    if st.button("📘 Self-Teach"):
        run_task(self_teach, "Self-Teach")
with col3:
    if st.button("🛠️ Self-Correct"):
        run_task(self_correct, "Self-Correct")
with col4:
    if st.button("🚀 Self-Improve"):
        run_task(self_improve, "Self-Improve")

# ========== SYSTEM LOGS ==========
st.subheader("📜 Live System Logs")
with st.expander("View Logs", expanded=True):
    for log_entry in st.session_state["logs"][-100:]:
        st.text(log_entry)
if st.button("🧹 Clear Logs"):
    st.session_state["logs"] = []

# ========== MEMORY MODULE ==========
st.subheader("🧠 Self-Reflective Memory")
st.json(st.session_state["memory"], expanded=False)
if st.download_button("📤 Export Memory as JSON", data=json.dumps(st.session_state["memory"], indent=2),
                     file_name="ai_memory.json", mime="application/json"):
    log("📦 Memory exported to file.")

# ========== DASHBOARD ==========
st.subheader("📊 Task Activity Dashboard")
for k, v in st.session_state["task_counts"].items():
    st.metric(label=k, value=v)
