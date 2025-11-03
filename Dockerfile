# Utiliser une image Python officielle légère
FROM public.ecr.aws/docker/library/python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/* \
    && git clone https://github.com/nazimboudeffa/card-scanner-fr-flask.git . \
    && pip3 install -r requirements.txt

# Exposer le port de Flask
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "app.py"]