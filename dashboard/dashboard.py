import streamlit as st
import plotly.express as px
import pandas as pd
import asyncio
import websockets

st.title("📊 Agent Performance Dashboard")

# Dummy data
df = pd.DataFrame({
    "agent": ["Diagnostics", "Learning", "Correction"],
    "tasks_completed": [10, 7, 5]
})

fig = px.bar(df, x="agent", y="tasks_completed", title="Tasks Completed by Agent")
st.plotly_chart(fig)

# WebSocket real-time updates (stub)
async def listen_updates():
    uri = "ws://backend:8001/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            st.write(msg)

if False:
    asyncio.run(listen_updates())
