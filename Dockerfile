# Image Python officielle slim
FROM public.ecr.aws/docker/library/python:3.12-slim

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cloner le repo séparément
RUN git clone https://github.com/nazimboudeffa/card-scanner-fr-flask.git .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port Flask
EXPOSE 5000

# Commande pour lancer l'application
ENTRYPOINT ["python", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]