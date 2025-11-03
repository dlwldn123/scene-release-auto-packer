# 📝 TodoList Ultra-Détaillée - eBook Scene Packer v2

**Date de création** : 2025-11-01  
**Basé sur** : `docs/cdc.md`

---

## 📊 Vue d'Ensemble

Cette todoList découpe le projet en **phases**, **étapes** et **sous-étapes** ultra-détaillées avec dépendances, estimations et critères de validation.

**Total estimé** : ~245 tâches réparties sur 9 phases

---

## Phase 0 : Préparation (1 semaine) ✅

### Étape 0.1 : Backup v1/ ✅
- ✅ Répertoire `backup/v1/` créé avec copie complète de `v1/`
- ✅ Historique Git initialisé dans `backup/v1/.git`
- ✅ Structure vérifiée (fichiers et dossiers présents)

### Étape 0.2 : Documentation Structurée ✅
- ✅ `docs/cdc.md`, `docs/DEVBOOK.md`, `docs/todolist.md`
- ✅ PRDs 001 → 007 + README
- ✅ `docs/BACKLOG_AGILE.md`, `docs/PROJECT_OVERVIEW.md`, `docs/TEST_PLAN.md`
- ✅ `docs/RISKS_REGISTER.md`, `docs/DEPLOYMENT_PLAN.md`, `docs/MCP_TOOLS_GUIDE.md`

### Étape 0.3 : Configuration Environnement Développement ✅
- ✅ Installation dépendances (`requirements.txt`, `requirements-dev.txt`)
- ✅ `pytest.ini`, `.coveragerc`, `pyproject.toml`, `package.json`
- ✅ Scripts linters/formatteurs référencés (ruff, black, isort, eslint, prettier)

### Étape 0.4 : Setup TDD ✅
- ✅ Structure tests : `tests/phase0/`, `tests/e2e/phase0/`
- ✅ Tests de validation Phase 0 écrits (unit + e2e)
- ✅ Couverture ≥ 90% vérifiée

### Étape 0.5 : Règles Cursor ✅
- ✅ Règles critiques chargées (`definition-of-done`, `tdd-methodology`, `testing-requirements`, `mcp-tools-usage`, etc.)
- ✅ Règles UX/UI 2025, services métier, modèles ORM, blueprints API

### Étape 0.6 : Validation & Documentation ✅
- ✅ Tests unitaires/intégration/E2E verts
- ✅ DEVBOOK Phase 0 marquée terminée
- ✅ TodoList Phase 0 à jour

**Critères de validation consolidés** :
- ✅ Couverture Phase 0 ≥ 90%
- ✅ Documentation à jour (DEVBOOK, TodoList, README)
- ✅ Aucune tâche Phase 0 restante

## Phase 1 : Infrastructure Core (2 semaines) ✅

### Étape 1.1 : Setup Flask App Factory ✅
- ✅ Structure `web/` (app factory, config, blueprints, extensions)
- ✅ `.env.example` documenté + chargement automatique via python-dotenv
- ✅ Tests : `tests/phase1/test_app_factory.py`

### Étape 1.2 : Base de Données MySQL ✅
- ✅ SQLAlchemy + Flask-Migrate initialisés (`web/extensions.py`)
- ✅ Modèles de base créés (`User`, `Role`, `Group`, `Permission`, `TokenBlocklist`)
- ✅ Structure Alembic `migrations/` + première migration `0001_initial_schema`
- ✅ Script d'initialisation (`scripts/init_db.py`) avec seed admin
- ✅ Tests : `tests/phase1/test_database.py`

### Étape 1.3 : Authentification JWT ✅
- ✅ Blueprint `auth` (login, refresh, logout, me)
- ✅ Callbacks JWT (revocation, erreurs, lookup user)
- ✅ TokenBlocklist persistant
- ✅ Tests : `tests/phase1/test_authentication.py`

### Étape 1.4 : Modèles de Base ✅
- ✅ Méthodes de hashing + relations many-to-many
- ✅ Tests ORM complets (`tests/phase1/test_models.py`)
- ✅ Migrations compatibles + seed admin via script
- ✅ Couverture cumulée à 98 %

## Phase 2 : Interface Administration (3 semaines)

### Étape 2.1 : Dashboard

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 3 jours  
**Dépendances** : Phase 1

#### Sous-étapes

##### 2.1.1 : Setup React
- ⏳ Installer React + dependencies
- ⏳ Créer structure src/
- ⏳ Configurer webpack/vite
- ⏳ Configurer routing (React Router)

##### 2.1.2 : Composant Dashboard
- ⏳ Créer Dashboard component
- ⏳ Afficher informations utilisateur connecté
- ⏳ Afficher statistiques basiques
- ⏳ Styling Bootstrap

##### 2.1.3 : API Dashboard
- ⏳ Créer endpoint GET /api/dashboard/stats
- ⏳ Retourner stats (releases count, etc.)
- ⏳ Sécuriser endpoint (JWT)
- ⏳ Tests endpoint

**Tests TDD** :
```python
def test_dashboard_stats():
    token = get_admin_token()
    response = client.get('/api/dashboard/stats',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'releases_count' in response.json
```

**Critères de validation** :
- Dashboard s'affiche
- Stats affichées
- API fonctionnelle
- Tests passent

---

### Étape 2.2 : Navigation

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 2 jours  
**Dépendances** : Étape 2.1

#### Sous-étapes

##### 2.2.1 : Composant Navigation
- ⏳ Créer Navbar component
- ⏳ Ajouter liens (Nouvelle Release, Liste, Rules, etc.)
- ⏳ Gérer état actif
- ⏳ Styling Bootstrap

##### 2.2.2 : React Router
- ⏳ Configurer routes principales
- ⏳ Créer route components (placeholders)
- ⏳ Tester navigation
- ⏳ Gérer 404

**Critères de validation** :
- Navigation fonctionnelle
- Routes configurées
- Navigation au clavier
- Tests passent

---

### Étape 2.3 : Structure Pages

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 2 jours  
**Dépendances** : Étape 2.2

#### Sous-étapes

##### 2.3.1 : Layout Page
- ⏳ Créer PageLayout component
- ⏳ Structure : Header (titre) + Description + Content
- ⏳ Réutilisable pour toutes pages
- ⏳ Styling

##### 2.3.2 : Pages Placeholders
- ⏳ Créer NouvelleReleasePage (structure)
- ⏳ Créer ListeReleasesPage (structure)
- ⏳ Créer RulesPage (structure)
- ⏳ Créer UtilisateursPage (structure)
- ⏳ Créer RolesPage (structure)
- ⏳ Créer ConfigurationsPage (structure)

**Critères de validation** :
- Toutes pages ont titre + description
- Layout cohérent
- Tests passent

---

### Étape 2.4 : Thème Jour/Nuit

**Statut** : ⏳ Non commencée  
**Priorité** : Should Have  
**Estimation** : 1 jour  
**Dépendances** : Étape 2.2

#### Sous-étapes

##### 2.4.1 : Context Theme
- ⏳ Créer ThemeContext
- ⏳ Gérer état theme (light/dark)
- ⏳ Persister dans localStorage
- ⏳ Provider theme

##### 2.4.2 : Composant Toggle
- ⏳ Créer ThemeToggle component
- ⏳ Bouton bascule jour/nuit
- ⏳ Icon soleil/lune
- ⏳ Styling

##### 2.4.3 : Styles Dark Mode
- ⏳ Créer variables CSS dark mode
- ⏳ Appliquer classes conditionnelles
- ⏳ Tester tous composants
- ⏳ Transition smooth

**Critères de validation** :
- Toggle fonctionne
- Thème appliqué partout
- Persistance localStorage
- Tests passent

---

**Note** : Les phases suivantes (3-9) seront détaillées de la même manière.  
**Voir** : `docs/PRDs/` pour détails fonctionnels de chaque fonctionnalité.

---

## 📈 Métriques

- **Total tâches** : 245 (estimation)
- **Tâches terminées** : 5
- **Tâches en cours** : 8
- **Tâches restantes** : 232
- **Progression** : ~2%

---

**Dernière mise à jour** : 2025-11-01  
**Prochaine mise à jour** : À chaque étape complétée

