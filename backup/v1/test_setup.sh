#!/bin/bash
# Script de test rapide pour valider l'installation
# Usage: ./test_setup.sh

set -e

echo "=== Test Scene Ebook Packer ==="
echo ""

# 1. Vérifier Python version
echo "1. Vérification Python..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Python 3.10+ requis, version détectée: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION OK (3.10+ requis)"
echo ""

# 2. Vérifier virtualenv activé (optionnel mais recommandé)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠ Virtualenv non activé (recommandé mais optionnel)"
else
    echo "✅ Virtualenv activé: $VIRTUAL_ENV"
fi
echo ""

# 3. Vérifier dépendances Python
echo "2. Vérification dépendances Python..."
python3 -c "
import sys
errors = []
missing = []

# Test imports critiques
try:
    import yaml
    print('✅ PyYAML OK')
except ImportError:
    missing.append('PyYAML')
    errors.append('PyYAML manquant')

try:
    import requests
    print('✅ Requests OK')
except ImportError:
    missing.append('requests')
    errors.append('Requests manquant')

try:
    import flask
    print('✅ Flask OK')
except ImportError:
    missing.append('flask')
    errors.append('Flask manquant (optionnel pour CLI)')

try:
    from bs4 import BeautifulSoup
    print('✅ BeautifulSoup4 OK')
except ImportError:
    missing.append('beautifulsoup4')
    errors.append('BeautifulSoup4 manquant')

try:
    from PIL import Image
    print('✅ Pillow OK')
except ImportError:
    missing.append('pillow')
    errors.append('Pillow manquant')

try:
    import PyPDF2
    print('✅ PyPDF2 OK')
except ImportError:
    missing.append('PyPDF2')
    errors.append('PyPDF2 manquant')

try:
    import ebookmeta
    print('✅ ebookmeta OK')
except ImportError:
    missing.append('ebookmeta')
    print('⚠ ebookmeta non disponible (fallback utilisé)')

try:
    import ebookatty
    print('✅ ebookatty OK')
except ImportError:
    missing.append('ebookatty')
    print('⚠ ebookatty non disponible (fallback utilisé)')

# Test imports modules locaux
try:
    from src.metadata.api_enricher import MetadataEnricher
    print('✅ Module API OK')
except ImportError as e:
    errors.append(f'Module API: {e}')

try:
    from src.packer import process_ebook
    print('✅ Module Packer OK')
except ImportError as e:
    errors.append(f'Module Packer: {e}')

if errors:
    print('')
    print('❌ Erreurs:')
    for err in errors:
        print(f'   - {err}')
    if missing:
        print('')
        print('📦 Installation manquante:')
        print(f'   pip install {\" \".join(missing)}')
    sys.exit(1)
" || exit 1
echo ""

# 4. Vérifier RAR
echo "3. Vérification RAR..."
if command -v rar &> /dev/null; then
    rar | head -1
    echo "✅ RAR CLI OK"
elif command -v unrar &> /dev/null; then
    unrar | head -1
    echo "✅ UnRAR CLI OK (note: création RAR nécessite rar CLI)"
else
    echo "⚠ RAR non installé (optionnel si rarfile Python utilisé)"
    echo "   Installation: sudo apt-get install rar"
fi
echo ""

# 5. Vérifier structure dossiers
echo "4. Vérification structure dossiers..."
REQUIRED_DIRS=("src" "web" "config" "templates")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/ existe"
    else
        echo "❌ $dir/ manquant"
        exit 1
    fi
done
echo ""

# 6. Test import modules complets
echo "5. Test import modules..."
python3 -c "
from src.metadata import detect_format, extract_epub_metadata
from src.packaging import create_rar_volumes, generate_nfo, generate_sfv, generate_diz, package_2022_format
from src.utils import generate_release_name, validate_release
from src.scene_rules import grab_rules_list, list_cached_rules
print('✅ Tous les modules importés avec succès')
" || {
    echo "❌ Erreur lors de l'import des modules"
    exit 1
}
echo ""

# 7. Test configuration
echo "6. Test chargement configuration..."
python3 -c "
from pathlib import Path
import yaml

config_path = Path('config/config.yaml')
if config_path.exists():
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    print('✅ Configuration YAML chargée')
else:
    print('⚠ config.yaml non trouvé (utilisera valeurs par défaut)')
" || echo "⚠ Erreur chargement config (utilisera valeurs par défaut)"
echo ""

echo "=== Tests terminés ==="
echo ""
echo "✅ Environnement prêt pour développement"
echo ""
echo "🚀 Pour tester complètement:"
echo "   python src/packer.py <ebook_file> -g TESTGRP --verbose"
echo ""
echo "🌐 Pour lancer l'interface web:"
echo "   python web/app.py"
echo "   ou: ./web/start.sh"
echo ""
echo "🧪 Pour lancer les tests unitaires:"
echo "   pytest tests/ -v"
echo ""
