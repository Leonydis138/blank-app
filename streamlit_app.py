# app.py (Gradio version for Hugging Face Spaces)
import gradio as gr
import openai
import threading
import time
import numpy as np
import faiss
import os
import pickle
from openai.embeddings_utils import get_embedding, cosine_similarity

# === CONFIG ===
openai.api_key = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-4o-mini"

# === MEMORY ===
memory_data = []
try:
    memory_index = faiss.read_index("memory.index")
    with open("memory.pkl", "rb") as f:
        memory_data = pickle.load(f)
except:
    memory_index = faiss.IndexFlatL2(1536)

# === SYSTEM PROMPTS ===
AGENT_PROMPT = "You are a helpful agent in an ongoing dialogue. Respond meaningfully."
OVERSEER_PROMPT = "You are the Overseer agent. Monitor Agent A and B, learn, and intervene when appropriate."

conversation = []
auto_mode = False

# === AGENT ===
def chat_completion(system, messages):
    try:
        response = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=[{"role": "system", "content": system}] + messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error: {e}]"

# === FAISS EMBED ===
def embed_and_store(text):
    try:
        vec = get_embedding(text, engine=EMBEDDING_MODEL)
        memory_index.add(np.array([vec], dtype='float32'))
        memory_data.append(text)
        with open("memory.pkl", "wb") as f:
            pickle.dump(memory_data, f)
        faiss.write_index(memory_index, "memory.index")
    except Exception as e:
        print(f"Embed error: {e}")

# === CONVERSATION ===
def step():
    global conversation
    turn = len(conversation)
    agent = "Agent A" if turn % 2 == 0 else "Agent B"
    msgs = [{"role": "assistant", "content": m['text']} for m in conversation]
    reply = chat_completion(AGENT_PROMPT, msgs)
    conversation.append({"agent": agent, "text": reply})
    embed_and_store(reply)
    return format_convo(), ""

def format_convo():
    return "\n".join([f"**{m['agent']}**: {m['text']}" for m in conversation])

# === OVERSEER ===
def overseer_respond(query):
    try:
        qvec = get_embedding(query, engine=EMBEDDING_MODEL)
        sims = cosine_similarity(qvec, [get_embedding(m, engine=EMBEDDING_MODEL) for m in memory_data])
        top_idxs = np.argsort(sims)[-3:][::-1]
        context = "\n".join([memory_data[i] for i in top_idxs])
        msgs = [{"role": "user", "content": f"Context:\n{context}\nQuestion:{query}"}]
        return chat_completion(OVERSEER_PROMPT, msgs)
    except Exception as e:
        return f"[Overseer Error: {e}]"

# === AUTO LOOP ===
def auto_loop():
    global auto_mode
    while auto_mode:
        step()
        time.sleep(5)

# === GRADIO UI ===
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Tri-Agent Conversational AI (Hugging Face Edition)")
    with gr.Row():
        convo_display = gr.Markdown(value="")
        step_btn = gr.Button("Manual Step")
        auto_btn = gr.Button("Toggle Auto Mode")

    with gr.Accordion("🧠 Overseer Panel", open=False):
        qbox = gr.Textbox(label="Ask the Overseer")
        overseer_out = gr.Textbox(label="Overseer's Response")

    def toggle_auto():
        global auto_mode
        auto_mode = not auto_mode
        if auto_mode:
            threading.Thread(target=auto_loop, daemon=True).start()
        return "Auto Mode: ON" if auto_mode else "Auto Mode: OFF"

    step_btn.click(step, outputs=[convo_display, overseer_out])
    qbox.submit(overseer_respond, inputs=qbox, outputs=overseer_out)
    auto_btn.click(toggle_auto, outputs=auto_btn)

demo.launch()
