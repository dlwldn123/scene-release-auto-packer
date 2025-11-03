#!/bin/bash
# Script de démarrage et test du serveur Flask

cd "$(dirname "$0")/.."

# Activer venv
source venv/bin/activate

# Vérifier que la base de données est initialisée
if [ ! -f ".db_initialized" ]; then
    echo "Initialisation de la base de données..."
    python3 web/scripts/init_db.py
    touch .db_initialized
fi

# Démarrer le serveur
echo "Démarrage du serveur Flask sur http://localhost:5000"
python3 web/app.py
