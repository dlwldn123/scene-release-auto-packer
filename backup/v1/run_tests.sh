#!/bin/bash
# Script de test complet pour Scene Packer

set -e

echo "=========================================="
echo "Tests Scene Packer - Implémentation"
echo "=========================================="

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier environnement
echo -e "\n${YELLOW}1. Vérification environnement...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtualenv non trouvé${NC}"
    exit 1
fi

source venv/bin/activate

# Tests unitaires
echo -e "\n${YELLOW}2. Tests unitaires...${NC}"
PYTHONPATH=. DATABASE_URL='sqlite:///test.db' python3 tests/test_implementation.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tests unitaires passés${NC}"
else
    echo -e "${RED}✗ Tests unitaires échoués${NC}"
    exit 1
fi

# Tests API (si serveur démarré)
echo -e "\n${YELLOW}3. Tests API...${NC}"
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    python3 tests/test_api.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Tests API passés${NC}"
    else
        echo -e "${RED}✗ Tests API échoués${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Serveur non démarré - tests API skippés${NC}"
    echo "Pour tester l'API, démarrez le serveur:"
    echo "  DATABASE_URL='sqlite:///test.db' python web/app.py"
fi

# Tests CLI
echo -e "\n${YELLOW}4. Tests CLI...${NC}"
if PYTHONPATH=. python3 src/packer_cli.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CLI fonctionne${NC}"
else
    echo -e "${RED}✗ CLI ne fonctionne pas${NC}"
    exit 1
fi

echo -e "\n${GREEN}=========================================="
echo "Tous les tests sont passés!"
echo "==========================================${NC}"
