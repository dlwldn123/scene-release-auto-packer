#!/usr/bin/env bash
# Script de démarrage complet avec vérifications

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Couleurs pour output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Démarrage Packer de Release${NC}"
echo ""

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker n'est pas installé${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose n'est pas installé${NC}"
    exit 1
fi

# Vérifier si .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ Fichier .env introuvable, création depuis .env.example${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ Veuillez modifier .env avec vos valeurs avant de continuer${NC}"
        echo -e "${YELLOW}⚠ Génération de clés sécurisées recommandée:${NC}"
        echo -e "   ${BLUE}openssl rand -hex 32${NC}"
        exit 1
    else
        echo -e "${RED}✗ Fichier .env.example introuvable${NC}"
        exit 1
    fi
fi

# Vérifier Python si disponible
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}📋 Vérification environnement...${NC}"
    python3 check_environment.py || {
        echo -e "${YELLOW}⚠ Certaines vérifications ont échoué, continuons quand même...${NC}"
    }
    echo ""
fi

# Démarrer les services
echo -e "${GREEN}📦 Démarrage des services Docker...${NC}"
docker-compose up -d --build

# Attendre que MySQL soit prêt
echo -e "${GREEN}⏳ Attente que MySQL soit prêt...${NC}"
sleep 5

# Vérifier health check
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T mysql mysqladmin ping -h localhost -u root -p"${MYSQL_ROOT_PASSWORD:-rootpassword}" &> /dev/null; then
        echo -e "${GREEN}✓ MySQL est prêt${NC}"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ MySQL n'est pas prêt après ${max_attempts} tentatives${NC}"
    exit 1
fi

# Initialiser la base de données
echo -e "${GREEN}🗄️  Initialisation de la base de données...${NC}"
docker-compose exec -T backend python web/scripts/init_db.py || {
    echo -e "${YELLOW}⚠ La base de données semble déjà initialisée${NC}"
}

# Vérifier si admin existe
echo -e "${GREEN}👤 Vérification utilisateur admin...${NC}"
if ! docker-compose exec -T backend python -c "from web.app import create_app; from web.database import db; from web.models.user import User; app = create_app(); app.app_context().push(); print('Admin exists:', User.query.filter_by(username='admin').first() is not None)" 2>/dev/null | grep -q "True"; then
    echo -e "${YELLOW}⚠ Création utilisateur admin par défaut...${NC}"
    docker-compose exec -T backend python web/scripts/seed_admin.py admin admin || {
        echo -e "${YELLOW}⚠ L'utilisateur admin existe déjà${NC}"
    }
fi

# Créer templates par défaut
echo -e "${GREEN}📝 Création templates NFO par défaut...${NC}"
docker-compose exec -T backend python web/scripts/seed_templates.py || {
    echo -e "${YELLOW}⚠ Erreur création templates (non critique)${NC}"
}

# Vérifier health check backend
echo -e "${GREEN}🏥 Vérification health check backend...${NC}"
sleep 3
max_attempts=10
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:5000/health &> /dev/null; then
        echo -e "${GREEN}✓ Backend est prêt${NC}"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

echo ""
echo -e "${GREEN}✅ Services démarrés avec succès!${NC}"
echo ""
echo -e "📋 Informations:"
echo -e "   - Interface Web: ${GREEN}http://localhost:5000${NC}"
echo -e "   - API: ${GREEN}http://localhost:5000/api${NC}"
echo -e "   - Health Check: ${GREEN}http://localhost:5000/health${NC}"
echo ""
echo -e "🔧 Commandes utiles:"
echo -e "   - Voir les logs: ${YELLOW}docker-compose logs -f${NC}"
echo -e "   - Arrêter: ${YELLOW}docker-compose down${NC}"
echo -e "   - Redémarrer: ${YELLOW}docker-compose restart${NC}"
echo -e "   - Accéder au shell: ${YELLOW}docker-compose exec backend bash${NC}"
echo ""
echo -e "📚 Documentation:"
echo -e "   - Guide démarrage: ${BLUE}QUICKSTART.md${NC}"
echo -e "   - Guide déploiement: ${BLUE}DEPLOYMENT.md${NC}"
echo ""