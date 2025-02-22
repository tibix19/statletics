# Utilise une image Python slim
FROM python:3.13.2-slim

# Définir le répertoire de travail
WORKDIR /app-backend

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'ensemble du code
COPY . .

# Exposer le port utilisé par le backend (ex: 8000)
EXPOSE 8000

# Commande pour démarrer l'application avec uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
