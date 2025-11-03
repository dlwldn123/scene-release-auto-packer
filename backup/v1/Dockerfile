# Dockerfile pour l'application Flask
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=web.app \
    FLASK_ENV=production

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    mediainfo \
    rar \
    && rm -rf /var/lib/apt/lists/*

# Créer répertoire application
WORKDIR /app

# Copier requirements et installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier application
COPY . .

# Créer répertoires nécessaires
RUN mkdir -p /app/releases /app/uploads /app/logs

# Utilisateur non-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exposer port
EXPOSE 5000

# Commande par défaut (gunicorn pour production)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "web.app:create_app()"]
