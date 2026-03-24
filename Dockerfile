FROM python:3.11-slim

WORKDIR /app

# Mettre à jour pip et installer les dépendances
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers du projet
COPY . .

# Exposer le port cloud par défaut (Hugging Face / Render)
EXPOSE 7860

# Démarrer le backend FastAPI pur (sans Streamlit)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
