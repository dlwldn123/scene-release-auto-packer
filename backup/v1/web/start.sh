#!/bin/bash
# Script démarrage interface web Flask

cd "$(dirname "$0")/.." || exit

echo "🚀 Démarrage Scene Packer..."

# Activer virtualenv si présent
if [ -d "venv" ]; then
    echo "📦 Activation du virtualenv..."
    source venv/bin/activate
    echo "✅ Virtualenv activé"
else
    echo "⚠️  Virtualenv non trouvé, utilisation de Python système"
fi

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé. Veuillez l'installer."
    exit 1
fi

export PYTHONPATH="$(pwd)"
echo "📁 PYTHONPATH: $PYTHONPATH"

# Démarrer Flask via app factory runner
echo "🌐 Démarrage du serveur Flask..."
echo "📍 Accédez à l'interface sur: http://localhost:5000"
echo ""
python3 web/app.py
