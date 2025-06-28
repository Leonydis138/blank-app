# Frontend
FROM python:3.10-slim as frontend
WORKDIR /app
COPY app.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Backend
FROM python:3.10-slim as backend
WORKDIR /backend
COPY backend/backend_requirements.txt backend/
RUN pip install --no-cache-dir -r backend/backend_requirements.txt
COPY backend/main.py backend/
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
