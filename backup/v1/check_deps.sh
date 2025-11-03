#!/bin/bash
# Script de vérification et installation des dépendances

cd "$(dirname "$0")/.." || exit

echo "🔍 Vérification des dépendances..."

# Activer virtualenv si présent
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtualenv non trouvé. Création..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Vérifier si requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt non trouvé!"
    exit 1
fi

# Installer/actualiser les dépendances
echo "📦 Installation des dépendances..."
pip install -q --upgrade pip
pip install -r requirements.txt

# Vérifier les dépendances critiques
echo ""
echo "✅ Vérification des modules critiques..."

CHECK_MODULES=(
    "flask"
    "flask_cors"
    "flask_caching"
    "flask_compress"
    "marshmallow"
    "ebookmeta"
    "ebookatty"
    "PyPDF2"
    "yaml"
    "PIL"
    "requests"
    "bs4"
)

MISSING=0
for module in "${CHECK_MODULES[@]}"; do
    if python3 -c "import $module" 2>/dev/null; then
        echo "  ✅ $module"
    else
        echo "  ❌ $module - MANQUANT"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "⚠️  $MISSING module(s) manquant(s). Réinstallation..."
    pip install -r requirements.txt --force-reinstall
fi

echo ""
echo "✅ Vérification terminée!"
echo ""
echo "Pour démarrer l'application:"
echo "  ./web/start.sh"
echo "  ou"
echo "  source venv/bin/activate && export PYTHONPATH=\$(pwd) && python3 web/app.py"
