# 🗺️ ROADMAP D'EXÉCUTION - Tests Exhaustifs

**Date** : 2025-01-27  
**Objectif** : Exécuter 300+ tests de manière structurée et documentée  
**Statut** : 📋 **PRÊT POUR DÉMARRAGE**

---

## 🎯 VUE D'ENSEMBLE

Cette roadmap détaille **l'ordre logique d'exécution** des tests exhaustifs définis dans `PLAN_TESTS_EXHAUSTIF.md`.

**Principe** : Commencer par les **fondations (Docker)**, puis **l'interface (Web)**, et enfin **le cœur métier (Packaging)**.

---

## 📅 PHASE 0 : PRÉPARATION (30 minutes)

### Objectifs
- Préparer l'environnement de test
- Vérifier tous les prérequis
- Créer outils de suivi

### Actions

#### 0.1 Vérification Environnement
- [ ] **PR0.001** : Vérifier Docker installé
  ```bash
  docker --version
  docker-compose --version
  ```
- [ ] **PR0.002** : Vérifier Python 3.11+ installé
  ```bash
  python3 --version
  ```
- [ ] **PR0.003** : Vérifier espace disque (>20GB)
  ```bash
  df -h
  ```
- [ ] **PR0.004** : Vérifier ports disponibles
  ```bash
  netstat -an | grep -E ':(3306|5000)'
  ```
- [ ] **PR0.005** : Vérifier fichier `.env` configuré
  ```bash
  test -f .env && echo "✅ .env existe" || echo "❌ .env manquant"
  ```

#### 0.2 Création Outils de Suivi
- [ ] **PR0.006** : Créer fichier `TESTS_PROGRESSION.md` (suivi manuel)
- [ ] **PR0.007** : Créer dossier `tests_results/` pour résultats
- [ ] **PR0.008** : Préparer fichiers de test (eBooks, vidéos, docs)

#### 0.3 Documentation Initiale
- [ ] **PR0.009** : Lire `PLAN_TESTS_EXHAUSTIF.md` complètement
- [ ] **PR0.010** : Comprendre structure tests (T01.xxx, T02.xxx, T03.xxx)

**Durée estimée** : 30 minutes  
**Statut** : ⏳ En attente

---

## 🐳 PHASE 1 : TESTS DOCKER (4-6 heures)

### Objectif
Valider que l'infrastructure Docker fonctionne à 100% avant de tester l'application.

### Ordre d'Exécution

#### 1.1 Prérequis et Infrastructure (30 min)
**Tests** : T01.001 à T01.006  
**Action** : Vérifier environnement, Dockerfile, build

```bash
# Commande de démarrage
./start_docker.sh

# Ou manuellement
docker-compose up -d --build
```

**Documentation** : Noter résultats dans `TESTS_PROGRESSION.md`

#### 1.2 Build et Image Docker (45 min)
**Tests** : T01.007 à T01.021  
**Action** : Valider build, image, sécurité

```bash
# Build image
docker-compose build backend

# Vérifier taille
docker images | grep packer

# Scan sécurité (si trivy installé)
trivy image ebook-scene-packer-backend:latest
```

#### 1.3 Services Docker Compose (1h)
**Tests** : T01.022 à T01.048  
**Action** : Valider MySQL, Backend, configuration

```bash
# Vérifier services
docker-compose ps

# Logs MySQL
docker-compose logs mysql

# Logs Backend
docker-compose logs backend

# Health checks
curl http://localhost:5000/health
```

#### 1.4 Intégration Docker (1h)
**Tests** : T01.049 à T01.062  
**Action** : Valider connexions, persistance, réseau

```bash
# Test connexion Backend → MySQL
docker-compose exec backend python -c "from web.database import db; from web.app import create_app; app = create_app(); app.app_context().push(); print('✅ DB OK')"

# Test persistance
docker-compose down
docker-compose up -d
# Vérifier données conservées
```

#### 1.5 Performance et Sécurité (45 min)
**Tests** : T01.063 à T01.073  
**Action** : Mesurer performance, valider sécurité

```bash
# Performance
docker stats packer_backend packer_mysql

# Sécurité
docker-compose config | grep -E 'secret|password|key'
```

#### 1.6 Scripts et Dépannage (1h)
**Tests** : T01.074 à T01.091  
**Action** : Valider scripts, tester dépannage

```bash
# Test script
./start_docker.sh

# Dépannage
docker-compose restart backend
docker-compose exec backend bash
```

### Résultats Attendus
- ✅ 100% tests Docker passent
- ✅ Services démarrés et fonctionnels
- ✅ Health checks OK
- ✅ Persistance données validée

### Documenter
- Créer `tests_results/DOCKER_RESULTS.md`
- Noter tous les résultats (PASS/FAIL/SKIP)
- Captures d'écran si erreurs
- Logs pertinents

**Durée estimée** : 4-6 heures  
**Statut** : ⏳ En attente

---

## 🌐 PHASE 2 : TESTS INTERFACE WEB (6-8 heures)

### Objectif
Valider que l'interface web fonctionne à 100% : routes, authentification, fonctionnalités.

### Prérequis
- ✅ Phase 1 complétée (Docker fonctionnel)
- ✅ Services Docker démarrés
- ✅ Base de données initialisée
- ✅ Utilisateur admin créé

### Ordre d'Exécution

#### 2.1 Infrastructure Web (30 min)
**Tests** : T02.001 à T02.014  
**Action** : Vérifier routes, health checks

```bash
# Démarrer services si pas déjà fait
docker-compose up -d

# Tests manuels
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/login
```

#### 2.2 Authentification (1h)
**Tests** : T02.015 à T02.030  
**Action** : Tester login, logout, protection routes

```bash
# Test login via API
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Tests E2E automatisés
pytest tests/e2e/test_auth_flow.py -v
pytest tests/e2e/test_auth.py -v
```

#### 2.3 Dashboard (45 min)
**Tests** : T02.031 à T02.041  
**Action** : Valider dashboard, statistiques

```bash
# Tests E2E dashboard
pytest tests/e2e/test_dashboard.py -v

# Test API stats
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/dashboard/stats
```

#### 2.4 Wizard de Packaging (2h)
**Tests** : T02.042 à T02.075  
**Action** : Tester wizard complet (12 étapes)

```bash
# Tests E2E wizard
pytest tests/e2e/test_wizard_flow.py -v
pytest tests/e2e/test_wizard.py -v

# Tests manuels via navigateur (Playwright MCP recommandé)
```

#### 2.5 Gestion Jobs (1h)
**Tests** : T02.076 à T02.093  
**Action** : Valider liste jobs, détails, logs

```bash
# Tests API jobs
pytest tests/e2e/test_jobs.py -v

# Tests manuels
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/jobs
```

#### 2.6 Gestion Utilisateurs (1h)
**Tests** : T02.094 à T02.115  
**Action** : CRUD utilisateurs (admin uniquement)

```bash
# Tests E2E utilisateurs
pytest tests/e2e/test_users_management.py -v
```

#### 2.7 Préférences et Configuration (1h30)
**Tests** : T02.116 à T02.174  
**Action** : Préférences, chemins, destinations, templates, releases

```bash
# Tests E2E configuration
pytest tests/e2e/test_configuration.py -v
pytest tests/e2e/test_preferences.py -v
pytest tests/e2e/test_preferences_paths_destinations_playwright.py -v
```

#### 2.8 Responsive et UX (30 min)
**Tests** : T02.175 à T02.183  
**Action** : Valider responsive, accessibilité

```bash
# Tests manuels avec Playwright MCP
# Vérifier différentes résolutions
# Vérifier navigation clavier
# Vérifier contraste WCAG
```

### Résultats Attendus
- ✅ 100% tests Interface Web passent
- ✅ Toutes routes accessibles
- ✅ Authentification fonctionnelle
- ✅ Toutes fonctionnalités opérationnelles

### Documenter
- Créer `tests_results/WEB_RESULTS.md`
- Noter tous les résultats
- Captures d'écran navigation
- Logs API pertinents

**Durée estimée** : 6-8 heures  
**Statut** : ⏳ En attente (Phase 1 requise)

---

## 📦 PHASE 3 : TESTS PACKAGING RELEASE (5-7 heures)

### Objectif
Valider que le packaging de release fonctionne à 100% pour tous les formats.

### Prérequis
- ✅ Phase 1 complétée (Docker)
- ✅ Phase 2 complétée (Interface Web)
- ✅ Fichiers de test disponibles (eBooks, vidéos, docs)

### Ordre d'Exécution

#### 3.1 Packaging EBOOK (2h)
**Tests** : T03.001 à T03.062  
**Action** : Tester tous formats EBOOK, métadonnées, packaging

```bash
# Test packaging EPUB
python src/packer_cli.py pack tests/fixtures/sample.epub TESTGRP

# Test via API
curl -X POST http://localhost:5000/api/wizard/pack \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@tests/fixtures/sample.epub" \
  -F "group=TESTGRP" \
  -F "type=EBOOK"

# Tests unitaires
pytest tests/test_packaging.py -v
pytest tests/test_docs_packaging.py -v
```

#### 3.2 Packaging TV (2h)
**Tests** : T03.063 à T03.102  
**Action** : Tester packaging vidéo, profils, RAR

```bash
# Test packaging TV
python src/packer_cli.py pack-tv tests/fixtures/sample.mkv \
  "Test.Series.S01E01.720p.HDTV.x264-TESTGRP"

# Test via API
curl -X POST http://localhost:5000/api/tv/pack \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@tests/fixtures/sample.mkv" \
  -F "release_name=Test.Series.S01E01.720p.HDTV.x264-TESTGRP"

# Tests TV APIs
pytest tests/test_tv_apis.py -v
```

#### 3.3 Packaging DOCS (1h)
**Tests** : T03.103 à T03.124  
**Action** : Tester packaging documents

```bash
# Test packaging DOCS
python src/packer_cli.py pack-docs tests/fixtures/sample.pdf TESTGRP

# Tests unitaires DOCS
pytest tests/test_docs_packaging.py -v
```

#### 3.4 Intégration et Workflows (1h30)
**Tests** : T03.125 à T03.152  
**Action** : Tester workflows complets, jobs, uploads

```bash
# Tests intégration services
pytest tests/test_integration_services.py -v

# Test workflow complet via wizard
# [Utiliser interface web ou Playwright MCP]

# Test upload FTP (si configuré)
# [Configurer destination FTP/SFTP dans interface]
```

### Résultats Attendus
- ✅ 100% tests Packaging passent
- ✅ Tous formats packagés correctement
- ✅ Releases conformes Scene Rules 2022
- ✅ Jobs et logs fonctionnels

### Documenter
- Créer `tests_results/PACKAGING_RESULTS.md`
- Noter tous les résultats
- Vérifier fichiers releases générés
- Logs packaging pertinents

**Durée estimée** : 5-7 heures  
**Statut** : ⏳ En attente (Phases 1 et 2 requises)

---

## 📊 PHASE 4 : SYNTHÈSE ET RAPPORT FINAL (1-2 heures)

### Objectif
Consolider tous les résultats, générer rapport final.

### Actions

#### 4.1 Consolidation Résultats
- [ ] **SYN4.001** : Compiler résultats Phase 1 (Docker)
- [ ] **SYN4.002** : Compiler résultats Phase 2 (Interface Web)
- [ ] **SYN4.003** : Compiler résultats Phase 3 (Packaging)
- [ ] **SYN4.004** : Calculer taux de réussite global

#### 4.2 Analyse Problèmes
- [ ] **SYN4.005** : Lister tous les tests échoués
- [ ] **SYN4.006** : Catégoriser erreurs (critique/moyen/mineur)
- [ ] **SYN4.007** : Identifier causes racines
- [ ] **SYN4.008** : Prioriser corrections

#### 4.3 Rapport Final
- [ ] **SYN4.009** : Créer `RAPPORT_TESTS_FINAL.md`
- [ ] **SYN4.010** : Statistiques complètes
- [ ] **SYN4.011** : Liste problèmes avec solutions
- [ ] **SYN4.012** : Recommandations améliorations

**Durée estimée** : 1-2 heures  
**Statut** : ⏳ En attente (Phases 1-3 requises)

---

## 🔄 ORDRE D'EXÉCUTION RECOMMANDÉ

```
Phase 0 (Préparation)
    ↓
Phase 1 (Docker) ───────┐
    ↓                    │
Phase 2 (Interface Web) ─┤
    ↓                    │
Phase 3 (Packaging) ─────┤
    ↓                    │
Phase 4 (Synthèse) ──────┘
```

**Séquentiel** : Chaque phase dépend de la précédente.

---

## 📋 CHECKLIST GLOBALE

### Avant de Commencer
- [ ] Lire `PLAN_TESTS_EXHAUSTIF.md`
- [ ] Lire cette roadmap complète
- [ ] Vérifier prérequis Phase 0
- [ ] Créer outils de suivi

### Pendant Exécution
- [ ] Documenter chaque test (PASS/FAIL/SKIP)
- [ ] Capturer erreurs avec logs
- [ ] Noter temps d'exécution
- [ ] Faire commits réguliers

### Après Exécution
- [ ] Générer rapport final
- [ ] Corriger problèmes critiques
- [ ] Ré-exécuter tests échoués
- [ ] Valider 100% réussite

---

## 🎯 CRITÈRES DE SUCCÈS

| Phase | Critère de Succès |
|-------|-------------------|
| **Phase 1** | 100% tests Docker passent, services opérationnels |
| **Phase 2** | 100% tests Interface Web passent, toutes fonctionnalités OK |
| **Phase 3** | 100% tests Packaging passent, releases conformes |
| **Phase 4** | Rapport final complet, problèmes identifiés et documentés |

---

## 🛠️ OUTILS ET COMMANDES

### Suivi Progression
```bash
# Créer fichier suivi
touch TESTS_PROGRESSION.md

# Créer dossiers résultats
mkdir -p tests_results/{docker,web,packaging}
```

### Tests Automatisés
```bash
# Tests unitaires
pytest tests/test_*.py -v

# Tests intégration
pytest tests/test_integration_*.py -v

# Tests E2E
pytest tests/e2e/ -v

# Avec couverture
pytest --cov=web --cov=src --cov-report=html
```

### Docker
```bash
# Démarrer
./start_docker.sh

# Logs
docker-compose logs -f backend

# Shell
docker-compose exec backend bash

# Arrêter
docker-compose down
```

### Interface Web
```bash
# Démarrer local (alternative)
python web/app.py

# Test health
curl http://localhost:5000/health

# Test API
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/jobs
```

---

## 📝 NOTES IMPORTANTES

1. **Ne pas sauter de phases** : Chaque phase prépare la suivante
2. **Documenter immédiatement** : Ne pas attendre la fin pour noter résultats
3. **Faire commits réguliers** : Un commit par phase complétée
4. **Demander aide si bloqué** : Ne pas perdre trop de temps sur un test
5. **Prioriser critiques** : Corriger problèmes bloquants avant de continuer

---

**Roadmap créée le** : 2025-01-27  
**Statut** : ✅ **PRÊTE POUR DÉMARRAGE**  
**Prochaine étape** : **Phase 0 - Préparation**

