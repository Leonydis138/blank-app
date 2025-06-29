# Tri-Agent Conversational AI

This Gradio app hosts three AI agents: two chatting agents (A & B) and an Overseer that listens, learns, and can intervene.

## Deployment on Hugging Face Spaces

1. Create a new Space (Gradio SDK, Python).
2. Upload `app.py`, `requirements.txt`.
3. In Settings → Secrets, add `OPENAI_API_KEY`.
4. The app will auto-launch at https://huggingface.co/spaces/<username>/<space-name>.
