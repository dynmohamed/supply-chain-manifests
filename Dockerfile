# 1. Start m une image Python légère
FROM python:3.12-slim

# 2. Créer un répertoire de travail
WORKDIR /app

# 3. Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copier le dossier src et le modèle
COPY src/ ./src/
COPY models/ ./models/

# 5. Exposer le port (SAP AI Core utilise souvent 8080 par défaut)
EXPOSE 8080

# 6. Lancer l'application (en supposant que agent_api.py contient ton FastAPI/Flask)
CMD ["uvicorn", "src.agent_api:app", "--host", "0.0.0.0", "--port", "8080"]