
import streamlit as st
import gradio as gr
import threading
import time
from huggingface_hub import InferenceClient

# ─── SETUP INFERENCE CLIENT ─────────────────────────────────────────────
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")

# ─── DEFINE CHAT RESPONSE FUNCTION ──────────────────────────────────────
def respond(message, history: list[tuple[str, str]], system_message, max_tokens, temperature, top_p):
    messages = [{"role": "system", "content": system_message}]
    for user, assistant in history:
        if user:
            messages.append({"role": "user", "content": user})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    response = ""
    for msg in client.chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stream=True,
    ):
        token = msg.choices[0].delta.content
        response += token
        yield response

# ─── STREAMLIT APP ──────────────────────────────────────────────────────
st.set_page_config(page_title="Zephyr ChatBot", layout="wide")
st.title("💬 Zephyr Chat Interface in Streamlit")

# Info box
with st.expander("ℹ️ About this Demo"):
    st.markdown("""
    This app uses **Gradio + Hugging Face Hub** to stream responses from the `HuggingFaceH4/zephyr-7b-beta` chat model via the `huggingface_hub.InferenceClient`.

    - Streaming chat interface
    - Custom system prompt + parameters
    """)

# Container for Gradio ChatInterface
gr_container = st.container()

with gr_container:
    # Only run Gradio block when this app is executed directly or inside Streamlit
    with st.spinner("Launching chat interface..."):
        demo = gr.ChatInterface(
            fn=respond,
            additional_inputs=[
                gr.Textbox(value="You are a friendly chatbot.", label="System message"),
                gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max new tokens"),
                gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
                gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p (nucleus sampling)"),
            ],
            title="Chat with Zephyr 7B",
            description="Streamed response using Hugging Face Hub",
        )

        demo.launch(inline=True, share=False)  # inline=True allows embedding inside Streamlit
