#!/usr/bin/env bash
# Script d'exécution automatisée des tests Docker (Phase 1)
# Partie du plan de tests exhaustif

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

RESULTS_DIR="$PROJECT_DIR/tests_results"
DOCKER_RESULTS="$RESULTS_DIR/DOCKER_RESULTS.md"

echo -e "${BLUE}🐳 EXÉCUTION TESTS DOCKER - Phase 1${NC}"
echo ""

# Créer dossier résultats
mkdir -p "$RESULTS_DIR"

# Initialiser fichier résultats
cat > "$DOCKER_RESULTS" << EOF
# 🐳 RÉSULTATS TESTS DOCKER

**Date** : $(date '+%Y-%m-%d %H:%M:%S')
**Phase** : Phase 1 - Tests Docker
**Statut** : ⏳ En cours

---

## 📊 STATISTIQUES

| Catégorie | Total | Passés | Échoués | Ignorés | Taux |
|-----------|-------|--------|---------|---------|------|
| Prérequis | 6 | 0 | 0 | 0 | 0% |
| Dockerfile | 10 | 0 | 0 | 0 | 0% |
| Build | 5 | 0 | 0 | 0 | 0% |
| Services | 27 | 0 | 0 | 0 | 0% |
| Intégration | 14 | 0 | 0 | 0 | 0% |
| Performance | 5 | 0 | 0 | 0 | 0% |
| Sécurité | 6 | 0 | 0 | 0 | 0% |
| Scripts | 12 | 0 | 0 | 0 | 0% |
| Dépannage | 6 | 0 | 0 | 0 | 0% |
| **TOTAL** | **91** | **0** | **0** | **0** | **0%** |

---

## 📋 RÉSULTATS DÉTAILLÉS

EOF

# Compteurs
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0

# Fonction pour tester et documenter
test_check() {
    local test_id=$1
    local description=$2
    local command=$3
    local expected="${4:-}"
    
    TOTAL=$((TOTAL + 1))
    echo -ne "${BLUE}[$test_id]${NC} $description... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED=$((PASSED + 1))
        echo "- ✅ **$test_id** : $description - PASS" >> "$DOCKER_RESULTS"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED=$((FAILED + 1))
        echo "- ❌ **$test_id** : $description - FAIL" >> "$DOCKER_RESULTS"
        return 1
    fi
}

# Section 1.1 : Prérequis
echo -e "${YELLOW}=== Section 1.1 : Prérequis ===${NC}"
test_check "T01.001" "Docker installé" "docker --version"
test_check "T01.002" "Docker Compose installé" "docker compose version"
test_check "T01.003" "Docker daemon en cours" "docker info"
test_check "T01.004" "Espace disque suffisant" "[ \$(df -h . | awk 'NR==2 {print \$4}' | sed 's/G//') -gt 10 ]"
test_check "T01.005" "Port 3306 disponible" "! netstat -an | grep -q ':3306.*LISTEN' || [ \$(docker ps -a | grep -c packer_mysql) -gt 0 ]"
test_check "T01.006" "Port 5000 disponible" "! netstat -an | grep -q ':5000.*LISTEN' || [ \$(docker ps -a | grep -c packer_backend) -gt 0 ]"

echo ""

# Section 1.2 : Dockerfile
echo -e "${YELLOW}=== Section 1.2 : Validation Dockerfile ===${NC}"
test_check "T01.007" "Dockerfile existe" "test -f Dockerfile"
test_check "T01.008" "Dockerfile basé Python 3.11" "grep -q 'FROM python:3.11' Dockerfile"
test_check "T01.009" "Dockerfile installe dépendances système" "grep -q 'apt-get install' Dockerfile"
test_check "T01.010" "Requirements.txt copié" "grep -q 'COPY requirements.txt' Dockerfile"
test_check "T01.011" "Application copiée" "grep -q 'COPY.*\.' Dockerfile"
test_check "T01.012" "Répertoires créés" "grep -q 'mkdir -p' Dockerfile"
test_check "T01.013" "Utilisateur non-root créé" "grep -q 'useradd.*appuser' Dockerfile"
test_check "T01.014" "Permissions /app" "grep -q 'chown.*appuser' Dockerfile"
test_check "T01.015" "Port 5000 exposé" "grep -q 'EXPOSE 5000' Dockerfile"
test_check "T01.016" "CMD Gunicorn" "grep -q 'gunicorn' Dockerfile"

echo ""

# Section 1.3 : Build
echo -e "${YELLOW}=== Section 1.3 : Build Image ===${NC}"
test_check "T01.017" "docker-compose.yml existe" "test -f docker-compose.yml"
test_check "T01.018" "Services définis" "grep -q 'services:' docker-compose.yml && grep -q 'backend:' docker-compose.yml && grep -q 'mysql:' docker-compose.yml"
test_check "T01.019" "Volumes définis" "grep -q 'volumes:' docker-compose.yml"
test_check "T01.020" "Réseau défini" "grep -q 'networks:' docker-compose.yml"
echo -e "${YELLOW}⚠️  T01.021 : Scan sécurité (manuel avec trivy)${NC}"
SKIPPED=$((SKIPPED + 1))

echo ""

# Section 1.4 : Services
echo -e "${YELLOW}=== Section 1.4 : Services Docker Compose ===${NC}"
if docker compose ps | grep -q "packer_mysql.*Up"; then
    test_check "T01.027" "MySQL démarré" "docker compose ps | grep -q 'packer_mysql.*Up'"
    test_check "T01.030" "Health check MySQL" "docker compose exec -T mysql mysqladmin ping -h localhost -uroot -prootpassword 2>/dev/null | grep -q 'mysqld is alive'"
else
    echo -e "${YELLOW}⚠️  Services non démarrés, démarrer avec: docker compose up -d${NC}"
    SKIPPED=$((SKIPPED + 5))
fi

if docker compose ps | grep -q "packer_backend.*Up"; then
    test_check "T01.037" "Backend démarré" "docker compose ps | grep -q 'packer_backend.*Up'"
    test_check "T01.042" "Health check backend" "curl -sf http://localhost:5000/health > /dev/null"
else
    echo -e "${YELLOW}⚠️  Backend non démarré${NC}"
    SKIPPED=$((SKIPPED + 5))
fi

echo ""

# Résumé
echo -e "${BLUE}=== RÉSUMÉ ===${NC}"
echo -e "Total tests : $TOTAL"
echo -e "${GREEN}Passés : $PASSED${NC}"
echo -e "${RED}Échoués : $FAILED${NC}"
echo -e "${YELLOW}Ignorés : $SKIPPED${NC}"

if [ $TOTAL -gt 0 ]; then
    RATE=$((PASSED * 100 / TOTAL))
    echo -e "Taux de réussite : ${RATE}%"
fi

# Mettre à jour fichier résultats
cat >> "$DOCKER_RESULTS" << EOF

---

## 📊 RÉSUMÉ FINAL

- **Total** : $TOTAL
- **Passés** : $PASSED ✅
- **Échoués** : $FAILED ❌
- **Ignorés** : $SKIPPED ⚠️
- **Taux réussite** : $([ $TOTAL -gt 0 ] && echo "$((PASSED * 100 / TOTAL))%" || echo "0%")

---

## 📝 NOTES

- Tests automatiques exécutés le $(date '+%Y-%m-%d %H:%M:%S')
- Certains tests nécessitent services Docker démarrés
- Tests de build nécessitent docker compose build
- Tests de performance nécessitent monitoring

---

**Rapport généré par** : run_docker_tests.sh
EOF

echo ""
echo -e "${GREEN}✅ Résultats sauvegardés dans : $DOCKER_RESULTS${NC}"
echo ""
echo -e "${YELLOW}📝 Pour tests complets, consulter PLAN_TESTS_EXHAUSTIF.md${NC}"

