# 📝 TodoList Ultra-Détaillée - eBook Scene Packer v2

**Date de création** : 2025-11-01  
**Basé sur** : `docs/cdc.md`

---

## 📊 Vue d'Ensemble

Cette todoList découpe le projet en **phases**, **étapes** et **sous-étapes** ultra-détaillées avec dépendances, estimations et critères de validation.

**Total estimé** : ~245 tâches réparties sur 9 phases

---

## Phase 0 : Préparation (1 semaine)

### Étape 0.1 : Backup v1/ ✅

**Statut** : ✅ Terminée  
**Priorité** : Must Have  
**Estimation** : 30 min

#### Sous-étapes
- ✅ Créer répertoire v1/
- ✅ Copier tous les fichiers/dossiers (sauf .git) dans v1/
- ✅ Vérifier structure préservée
- ✅ Nettoyer fichiers doublons à la racine

**Critères de validation** :
- ✅ Aucun fichier à la racine sauf .git et v1/
- ✅ Tous les fichiers v1 présents dans v1/

---

### Étape 0.2 : Création Documentation Structurée 🔄

**Statut** : 🟡 En cours  
**Priorité** : Must Have  
**Estimation** : 2 jours

#### Sous-étapes

##### 0.2.1 : CDC (Cahier des Charges)
- ✅ Créer docs/cdc.md
- ✅ Documenter vision, objectifs, fonctionnalités
- ✅ Documenter contraintes techniques
- ✅ Documenter méthodologies

##### 0.2.2 : DEVBOOK
- ✅ Créer docs/DEVBOOK.md
- ⏳ Initialiser phases et étapes
- ⏳ Configurer OKRs
- ⏳ Créer journal modifications

##### 0.2.3 : TodoList
- 🟡 Créer docs/todolist.md (ce fichier)
- ⏳ Découper toutes les phases en sous-étapes
- ⏳ Ajouter dépendances
- ⏳ Ajouter estimations

##### 0.2.4 : PRDs (Product Requirement Documents)
- ⏳ Créer docs/PRDs/README.md
- ⏳ Créer PRD-001-Interface-Admin.md
- ⏳ Créer PRD-002-Nouvelle-Release.md
- ⏳ Créer PRD-003-Liste-Releases.md
- ⏳ Créer PRD-004-Rules.md
- ⏳ Créer PRD-005-Utilisateurs.md
- ⏳ Créer PRD-006-Roles.md
- ⏳ Créer PRD-007-Configurations.md

##### 0.2.5 : Backlog Agile
- ⏳ Créer docs/BACKLOG_AGILE.md
- ⏳ Définir Epics
- ⏳ Définir User Stories
- ⏳ Définir tâches techniques
- ⏳ Prioriser avec MoSCoW et Eisenhower

##### 0.2.6 : Project Overview
- ⏳ Créer docs/PROJECT_OVERVIEW.md
- ⏳ Documenter vision et portée
- ⏳ Documenter phases principales
- ⏳ Documenter méthodologies

##### 0.2.7 : Test Plan
- ⏳ Créer docs/TEST_PLAN.md
- ⏳ Documenter stratégie TDD
- ⏳ Documenter scénarios de test
- ⏳ Documenter outils et méthodologie

##### 0.2.8 : Risks Register
- ⏳ Créer docs/RISKS_REGISTER.md
- ⏳ Identifier risques techniques
- ⏳ Identifier risques fonctionnels
- ⏳ Analyser avec SWOT
- ⏳ Définir plans de mitigation

##### 0.2.9 : Deployment Plan
- ⏳ Créer docs/DEPLOYMENT_PLAN.md
- ⏳ Documenter pré-requis
- ⏳ Documenter étapes déploiement
- ⏳ Documenter rollback

**Critères de validation** :
- Tous les fichiers de documentation créés
- Documentation cohérente et complète
- Liens entre documents fonctionnels

---

### Étape 0.3 : Configuration Environnement Développement

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 1 jour

#### Sous-étapes

##### 0.3.1 : Environnement Python
- ⏳ Créer venv Python 3.11+
- ⏳ Installer dépendances (requirements.txt)
- ⏳ Installer dépendances dev (requirements-dev.txt)
- ⏳ Configurer pyproject.toml

##### 0.3.2 : Configuration IDE
- ⏳ Configurer Cursor/VS Code
- ⏳ Configurer extensions (Python, ESLint, etc.)
- ⏳ Configurer formatage automatique
- ⏳ Configurer linters

##### 0.3.3 : Docker (Optionnel)
- ⏳ Créer Dockerfile
- ⏳ Créer docker-compose.yml
- ⏳ Configurer services (Flask, MySQL)
- ⏳ Tester démarrage conteneurs

##### 0.3.4 : Git Configuration
- ⏳ Configurer .gitignore
- ⏳ Configurer .gitattributes
- ⏳ Créer branche v2
- ⏳ Configurer pre-commit hooks

**Critères de validation** :
- Environnement fonctionnel
- Tests de base passent
- Docker démarre (si configuré)

---

### Étape 0.4 : Setup TDD

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 1 jour

#### Sous-étapes

##### 0.4.1 : Installation Outils Tests
- ⏳ Installer pytest
- ⏳ Installer pytest-cov (coverage)
- ⏳ Installer pytest-mock
- ⏳ Installer pytest-flask

##### 0.4.2 : Configuration Tests
- ⏳ Créer structure tests/
- ⏳ Créer conftest.py
- ⏳ Configurer pytest.ini
- ⏳ Configurer .coveragerc

##### 0.4.3 : Fixtures de Base
- ⏳ Créer fixtures DB
- ⏳ Créer fixtures utilisateurs
- ⏳ Créer fixtures Flask app
- ⏳ Créer fixtures données de test

##### 0.4.4 : Test Exemple TDD
- ⏳ Écrire test échouant (Red)
- ⏳ Implémenter code minimal (Green)
- ⏳ Refactorer (Refactor)
- ⏳ Vérifier coverage 100%

**Critères de validation** :
- Tests passent
- Coverage configuré
- Cycle TDD validé

---

### Étape 0.5 : Règles Cursor

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 2 heures

#### Sous-étapes

##### 0.5.1 : Règles Projet
- ⏳ Créer .cursor/rules/project-v2.mdc
- ⏳ Documenter architecture v2
- ⏳ Documenter conventions de code
- ⏳ Documenter structure projet

##### 0.5.2 : Règles TDD
- ⏳ Créer .cursor/rules/tdd-methodology.mdc
- ⏳ Documenter cycle Red-Green-Refactor
- ⏳ Documenter exigences couverture
- ⏳ Documenter structure tests

##### 0.5.3 : Règles Documentation
- ⏳ Créer .cursor/rules/documentation-standards.mdc
- ⏳ Documenter format PRD
- ⏳ Documenter format DEVBOOK
- ⏳ Documenter mise à jour fichiers

##### 0.5.4 : Règles Tests
- ⏳ Créer .cursor/rules/testing-requirements.mdc
- ⏳ Documenter types tests
- ⏳ Documenter structure tests
- ⏳ Documenter mocks et fixtures

**Critères de validation** :
- Toutes les règles créées
- Règles activées dans Cursor
- Validation fonctionnement

---

## Phase 1 : Infrastructure Core (2 semaines)

### Étape 1.1 : Setup Flask App Factory

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 1 jour  
**Dépendances** : Phase 0

#### Sous-étapes

##### 1.1.1 : Structure Projet
- ⏳ Créer web/ directory
- ⏳ Créer web/app.py avec create_app()
- ⏳ Créer web/config.py
- ⏳ Créer web/__init__.py

##### 1.1.2 : Configuration Environnement
- ⏳ Créer .env.example
- ⏳ Créer web/config.py (Config, DevConfig, ProdConfig)
- ⏳ Configurer chargement .env (python-dotenv)
- ⏳ Tester configuration par environnement

##### 1.1.3 : Blueprints Structure
- ⏳ Créer web/blueprints/ directory
- ⏳ Créer structure blueprint (__init__.py)
- ⏳ Créer blueprint exemple (health)
- ⏳ Tester enregistrement blueprints

**Tests TDD** :
```python
# Test création app
def test_create_app_dev():
    app = create_app('development')
    assert app.config['DEBUG'] is True

def test_create_app_prod():
    app = create_app('production')
    assert app.config['DEBUG'] is False
```

**Critères de validation** :
- App se lance en dev/prod
- Configuration chargée correctement
- Blueprints enregistrés
- Tests passent

---

### Étape 1.2 : Base de Données MySQL

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 2 jours  
**Dépendances** : Étape 1.1

#### Sous-étapes

##### 1.2.1 : Configuration MySQL
- ⏳ Installer Flask-SQLAlchemy
- ⏳ Configurer connexion MySQL
- ⏳ Créer script init_db.py
- ⏳ Tester connexion DB

##### 1.2.2 : Models de Base
- ⏳ Créer web/models/ directory
- ⏳ Créer web/models/__init__.py
- ⏳ Créer User model (squelette)
- ⏳ Créer Role model (squelette)
- ⏳ Créer Group model (squelette)

##### 1.2.3 : Flask-Migrate
- ⏳ Installer Flask-Migrate
- ⏳ Initialiser migrations/
- ⏳ Créer première migration
- ⏳ Tester upgrade/downgrade

**Tests TDD** :
```python
def test_db_connection():
    from web.app import create_app
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        assert db.session.execute('SELECT 1').scalar() == 1
```

**Critères de validation** :
- Connexion DB fonctionnelle
- Models créés
- Migrations fonctionnelles
- Tests passent

---

### Étape 1.3 : Authentification JWT

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 3 jours  
**Dépendances** : Étape 1.2

#### Sous-étapes

##### 1.3.1 : Setup Flask-JWT-Extended
- ⏳ Installer Flask-JWT-Extended
- ⏳ Configurer JWT dans app
- ⏳ Configurer JWT_SECRET_KEY
- ⏳ Configurer JWT_ACCESS_TOKEN_EXPIRES

##### 1.3.2 : Endpoint Login
- ⏳ Créer blueprint auth
- ⏳ Créer endpoint POST /api/auth/login
- ⏳ Implémenter validation credentials
- ⏳ Générer tokens (access + refresh)

##### 1.3.3 : Endpoint Refresh
- ⏳ Créer endpoint POST /api/auth/refresh
- ⏳ Implémenter refresh token logic
- ⏳ Valider refresh token
- ⏳ Générer nouveau access token

##### 1.3.4 : Protection Routes
- ⏳ Créer décorateur @jwt_required()
- ⏳ Créer décorateur @admin_required()
- ⏳ Tester protection endpoints
- ⏳ Implémenter gestion erreurs JWT

##### 1.3.5 : Révocation Tokens
- ⏳ Créer modèle TokenBlacklist
- ⏳ Implémenter logout (blacklist)
- ⏳ Implémenter vérification blacklist
- ⏳ Tester révocation

**Tests TDD** :
```python
def test_login_success():
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'password'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_protected_route():
    token = get_token()
    response = client.get('/api/protected', 
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
```

**Critères de validation** :
- Login fonctionnel
- Refresh token fonctionnel
- Protection routes active
- Révocation fonctionnelle
- Tests passent

---

### Étape 1.4 : Modèles de Base

**Statut** : ⏳ Non commencée  
**Priorité** : Must Have  
**Estimation** : 3 jours  
**Dépendances** : Étape 1.2, Étape 1.3

#### Sous-étapes

##### 1.4.1 : Model User
- ⏳ Créer User model complet
- ⏳ Champs : id, username, note, password_hash, active, modify_at, created_at, created_by
- ⏳ Relation : groups, roles
- ⏳ Méthodes : hash_password, verify_password
- ⏳ Tests CRUD

##### 1.4.2 : Model Role
- ⏳ Créer Role model complet
- ⏳ Champs : id, name, description, created_at
- ⏳ Relation : users, permissions
- ⏳ Tests CRUD

##### 1.4.3 : Model Permission
- ⏳ Créer Permission model complet
- ⏳ Champs : id, role_id, resource, action (READ/WRITE/MOD)
- ⏳ Relation : role
- ⏳ Tests CRUD

##### 1.4.4 : Model Group
- ⏳ Créer Group model complet
- ⏳ Champs : id, name, description, created_at
- ⏳ Relation : users
- ⏳ Tests CRUD

##### 1.4.5 : Migrations
- ⏳ Générer migrations pour tous models
- ⏳ Tester upgrade
- ⏳ Tester downgrade
- ⏳ Créer données seed (admin user)

**Tests TDD** :
```python
def test_create_user():
    user = User(username='test', note='Test user')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    assert user.id is not None

def test_user_password():
    user = User(username='test', note='Test user')
    user.set_password('password')
    assert user.check_password('password') is True
```

**Critères de validation** :
- Tous models créés avec relations
- Migrations générées
- Tests CRUD passent
- Seed data créé

---

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

