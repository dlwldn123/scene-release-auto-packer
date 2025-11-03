#!/bin/bash
# Script d'installation Scene Ebook Packer
# Usage: ./INSTALL.sh

set -e

echo "=== Installation Scene Ebook Packer ==="
echo ""

# 1. Vérifier Python
echo "1. Vérification Python..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Python 3.10+ requis, version détectée: $PYTHON_VERSION"
    echo "   Installation: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION OK"
echo ""

# 2. Créer virtualenv (recommandé)
echo "2. Création virtualenv..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtualenv créé"
else
    echo "✅ Virtualenv existe déjà"
fi

echo ""
echo "Activation virtualenv..."
source venv/bin/activate
echo "✅ Virtualenv activé"
echo ""

# 3. Mettre à jour pip
echo "3. Mise à jour pip..."
pip install --upgrade pip
echo "✅ pip mis à jour"
echo ""

# 4. Installer dépendances Python
echo "4. Installation dépendances Python..."
pip install -r requirements.txt
echo "✅ Dépendances installées"
echo ""

# 5. Créer dossiers nécessaires
echo "5. Création dossiers..."
mkdir -p uploads releases ebooks rules_cache cache
echo "✅ Dossiers créés"
echo ""

# 6. Vérifier RAR (optionnel)
echo "6. Vérification RAR..."
if command -v rar &> /dev/null; then
    echo "✅ RAR CLI installé"
elif command -v unrar &> /dev/null; then
    echo "⚠ UnRAR CLI installé (création RAR nécessite rar CLI)"
    echo "   Installation: sudo apt-get install rar (Debian/Ubuntu)"
    echo "                  brew install rar (macOS)"
else
    echo "⚠ RAR non installé (optionnel)"
    echo "   Installation: sudo apt-get install rar (Debian/Ubuntu)"
    echo "                  brew install rar (macOS)"
fi
echo ""

# 7. Exécuter tests de validation
echo "7. Tests de validation..."
if [ -f "test_setup.sh" ]; then
    ./test_setup.sh
else
    echo "⚠ test_setup.sh non trouvé, skip"
fi
echo ""

echo "=== Installation terminée ==="
echo ""
echo "✅ Scene Ebook Packer installé avec succès"
echo ""
echo "📖 Documentation: README.md"
echo ""
echo "🚀 Commandes utiles:"
echo "   - CLI: python src/packer.py <ebook> -g GROUP"
echo "   - Web: python web/app.py ou ./web/start.sh"
echo "   - Tests: pytest tests/ -v"
echo ""
