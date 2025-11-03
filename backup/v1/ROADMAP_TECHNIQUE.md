# Roadmap Technique - Packer de Release Scene

## Analyse de l'État Actuel vs Objectifs

### ✅ Fonctionnalités Existantes

#### Backend Flask
- ✅ Application factory pattern (`create_app()`)
- ✅ Blueprints modulaires (`api`, `tv`)
- ✅ Extraction métadonnées (EPUB, PDF, MOBI/AZW/AZW3, CBZ)
- ✅ Packaging conforme EBOOK 2022 (ZIP + RAR + NFO + DIZ + SFV)
- ✅ Support TV (`pack_tv_release`)
- ✅ Enrichissement APIs (OpenLibrary, Google Books)
- ✅ Gestion règles Scene (scraping, cache)
- ✅ Validation releases
- ✅ Préférences basiques (fichier JSON `config/prefs.json`)
- ✅ Configuration YAML (`config/config.yaml`)
- ✅ Marshmallow schemas pour validation
- ✅ Gestion erreurs personnalisées

#### Frontend Web
- ✅ Interface Flask basique (HTML templates)
- ✅ Upload drag & drop
- ✅ Formulaire packaging
- ✅ Liste releases
- ✅ Visualisation règles Scene
- ✅ Gestion groupes Scene

#### CLI
- ✅ Script `src/packer.py` fonctionnel
- ✅ Support arguments ligne de commande
- ✅ Mode verbose

### 🔨 Fonctionnalités à Construire

#### Backend Flask
- ❌ Authentification JWT (Flask-JWT-Extended)
- ❌ Base de données MySQL (Flask-SQLAlchemy)
- ❌ Modèle de données (users, jobs, releases, preferences, api_configs, ftp_configs)
- ❌ Système de jobs avec tracking (ID UUID, logs par job)
- ❌ Chiffrement credentials (AES-GCM)
- ❌ Endpoints API jobs (`/api/jobs/*`)
- ❌ Endpoints API auth (`/api/auth/*`)
- ❌ Endpoints API config (`/api/config/apis`, `/api/config/ftp`)
- ❌ Enrichissement APIs TV (OMDb, TVDB, TMDb)
- ❌ Upload FTP/SFTP
- ❌ Journalisation structurée par job ID
- ❌ Migrations DB (Flask-Migrate)

#### Frontend React
- ❌ Application React complète
- ❌ Wizard multi-étapes (9 étapes)
- ❌ React Router pour navigation
- ❌ React Context API pour état global
- ❌ Composants wizard (StepGroup, StepReleaseType, etc.)
- ❌ Prévisualisation enrichie (arborescence, NFO rendu)
- ❌ Drag & drop amélioré (React Dropzone)
- ❌ Navigateur fichiers (tree view)
- ❌ Internationalisation (i18n FR/EN)
- ❌ Authentification UI (login/logout)
- ❌ Configuration UI (APIs, FTP)

#### CLI
- ❌ CLI complète avec sous-commandes (`packer pack`, `packer jobs`, etc.)
- ❌ Mode interactif avec prompts
- ❌ Commandes batch jobs (`list`, `show`, `rerun`, `logs`)
- ❌ Parité fonctionnelle avec Web
- ❌ Codes de sortie standardisés

#### Infrastructure
- ❌ Docker Compose
- ❌ Dockerfiles (frontend React, backend Flask)
- ❌ Configuration MySQL dans Docker
- ❌ Variables d'environnement (.env)
- ❌ Health checks

#### Tests
- ❌ Tests unitaires complets
- ❌ Tests intégration
- ❌ Tests E2E (wizard Web + CLI)
- ❌ Mocks APIs externes
- ❌ Golden files CLI

---

## Roadmap Détaillée par Sprint

### Sprint 1 : MVP - Base de Données et Authentification

**Objectif** : Mettre en place l'infrastructure de base (DB + Auth) pour les fonctionnalités avancées.

#### Backend
1. **Base de données MySQL**
   - [ ] Configurer Flask-SQLAlchemy
   - [ ] Créer modèles (User, Job, Release, Preference, ApiConfig, FtpConfig)
   - [ ] Configurer Flask-Migrate
   - [ ] Créer migrations initiales
   - [ ] Scripts d'initialisation DB (admin par défaut)

2. **Authentification JWT**
   - [ ] Installer Flask-JWT-Extended
   - [ ] Créer blueprint `auth` (`/api/auth/login`, `/api/auth/logout`, `/api/auth/me`)
   - [ ] Modèle User avec hash password (bcrypt)
   - [ ] Middleware protection endpoints API
   - [ ] Gestion rôles (admin/operator)

3. **Système de Jobs**
   - [ ] Modèle Job (UUID, status, config_json, log_path)
   - [ ] Créer job ID UUID lors démarrage packaging
   - [ ] Journalisation logs par job ID (`logs/<job_id>.log`)
   - [ ] Mettre à jour status job (pending → running → completed/failed)

#### Tests
- [ ] Tests authentification (login, logout, protection endpoints)
- [ ] Tests création jobs
- [ ] Tests journalisation logs

**Critères d'acceptation** :
- ✅ Utilisateur peut créer compte et se connecter
- ✅ Jobs créés avec UUID et logs par job ID
- ✅ Endpoints API protégés par JWT

---

### Sprint 2 : Wizard Web Multi-Étapes (React)

**Objectif** : Créer l'interface React wizard complète avec navigation par étapes.

#### Frontend React
1. **Setup React**
   - [ ] Initialiser projet React (Create React App ou Vite)
   - [ ] Configurer Bootstrap (CSS + JS)
   - [ ] Configurer React Router
   - [ ] Structure dossiers (`components/`, `contexts/`, `services/`)

2. **Composants Wizard**
   - [ ] `WizardContainer` : Container principal avec état global (Context)
   - [ ] `StepGroup` : Saisie nom groupe (validation format Scene)
   - [ ] `StepReleaseType` : Sélection type (TV, EBOOK, DOCS)
   - [ ] `StepRules` : Sélection règles Scene (chargement depuis API)
   - [ ] `StepFileSelection` : Upload (drag & drop) + URL distant
   - [ ] `StepMetadata` : Formulaire métadonnées + extraction auto
   - [ ] `StepNFO` : Sélection template + prévisualisation rendu
   - [ ] `StepSummary` : Résumé + édition manuelle
   - [ ] `StepResults` : Vue résultats + arborescence
   - [ ] Navigation (Previous/Next avec validation)

3. **API Service**
   - [ ] Service API client (fetch avec JWT token)
   - [ ] Intégration endpoints existants (`/api/meta`, `/api/pack`)
   - [ ] Gestion erreurs API

4. **Authentification UI**
   - [ ] Composant Login
   - [ ] Stockage JWT token (localStorage)
   - [ ] Protection routes wizard (requiert auth)

#### Backend
- [ ] Endpoint `/api/rules` : Liste règles Scene
- [ ] Endpoint `/api/preferences` : CRUD préférences utilisateur
- [ ] Adapter `/api/pack` pour retourner job ID

#### Tests
- [ ] Tests composants React (unitaires)
- [ ] Tests navigation wizard
- [ ] Tests intégration API

**Critères d'acceptation** :
- ✅ Wizard fonctionnel avec 9 étapes
- ✅ Navigation forward/backward
- ✅ Validation chaque étape
- ✅ Soumission packaging via API

---

### Sprint 3 : Enrichissement APIs et Prévisualisation

**Objectif** : Améliorer extraction métadonnées et prévisualisation enrichie.

#### Backend
1. **APIs Externes TV**
   - [ ] Intégration OMDb (série, saison, épisode)
   - [ ] Intégration TVDB (recherche + métadonnées)
   - [ ] Intégration TMDb (fallback)
   - [ ] Retry avec backoff (3 tentatives)
   - [ ] Timeout configurable (10s)

2. **MediaInfo**
   - [ ] Intégration MediaInfo CLI (extraction métadonnées vidéo)
   - [ ] Parsing sortie MediaInfo
   - [ ] Fallback si MediaInfo non disponible

3. **Enrichissement Métadonnées**
   - [ ] Endpoint `/api/metadata/enrich` (fusion APIs + locales)
   - [ ] Priorité API → locales
   - [ ] Cache résultats API (Flask-Caching)

#### Frontend
- [ ] Prévisualisation métadonnées enrichies (StepMetadata)
- [ ] Prévisualisation NFO rendu (StepNFO)
- [ ] Arborescence release (StepResults)
- [ ] Affichage thumbnails vidéo (si disponible)

#### Tests
- [ ] Tests intégration APIs externes (mocks)
- [ ] Tests enrichissement métadonnées

**Critères d'acceptation** :
- ✅ Métadonnées TV enrichies via OMDb/TVDB
- ✅ Prévisualisation NFO en temps réel
- ✅ Arborescence release affichée

---

### Sprint 4 : Configuration et Secrets

**Objectif** : Sécuriser et gérer configuration APIs et FTP.

#### Backend
1. **Chiffrement Credentials**
   - [ ] Module chiffrement AES-GCM
   - [ ] Clé dérivée depuis secret JWT (ou clé symétrique env)
   - [ ] Fonctions encrypt/decrypt credentials

2. **Configuration APIs**
   - [ ] Modèle ApiConfig (user_id, api_name, credentials_encrypted)
   - [ ] Endpoints `/api/config/apis` (GET/POST)
   - [ ] Chargement credentials décryptés lors appel API
   - [ ] Support OMDb, TVDB, TMDb, OpenLibrary

3. **Configuration FTP/SFTP**
   - [ ] Modèle FtpConfig (user_id, host, port, username, credentials_encrypted)
   - [ ] Endpoints `/api/config/ftp` (GET/POST)
   - [ ] Bibliothèque FTP/SFTP (paramiko pour SFTP, ftplib pour FTP)
   - [ ] Upload volumes vers serveur configuré

#### Frontend
- [ ] Composant Configuration (onglet dédié)
- [ ] Formulaire APIs (saisie clés API)
- [ ] Formulaire FTP/SFTP (saisie credentials)
- [ ] Liste configurations existantes

#### Tests
- [ ] Tests chiffrement/déchiffrement
- [ ] Tests upload FTP/SFTP (mock)

**Critères d'acceptation** :
- ✅ Clés API stockées chiffrées
- ✅ Credentials FTP/SFTP stockés chiffrés
- ✅ Upload release vers FTP/SFTP fonctionnel

---

### Sprint 5 : CLI Complète

**Objectif** : CLI avec parité fonctionnelle Web + batch jobs.

#### CLI
1. **Structure CLI**
   - [ ] Bibliothèque CLI (Click ou argparse avancé)
   - [ ] Commandes principales :
     - `packer pack <file>` : Packager fichier
     - `packer pack --interactive` : Mode interactif
     - `packer jobs list` : Liste jobs
     - `packer jobs show <job-id>` : Détail job
     - `packer jobs rerun <job-id>` : Ré-exécuter job
     - `packer jobs logs <job-id>` : Afficher logs
     - `packer config set/get` : Configuration
   - [ ] Parsing arguments + validation
   - [ ] Codes de sortie standardisés (0-255)

2. **Mode Interactif**
   - [ ] Prompts interactifs (groupe, type, fichiers, etc.)
   - [ ] Validation saisie utilisateur
   - [ ] Affichage progression

3. **Batch Jobs**
   - [ ] Appel API `/api/jobs/*` depuis CLI
   - [ ] Affichage liste jobs (format table)
   - [ ] Affichage logs job (fichier ou API)
   - [ ] Ré-exécution job (utilisation config_json sauvegardée)

#### Tests
- [ ] Tests CLI (unitaires + golden files)
- [ ] Tests mode interactif
- [ ] Tests batch jobs

**Critères d'acceptation** :
- ✅ CLI fonctionnelle avec toutes commandes
- ✅ Mode interactif guide utilisateur
- ✅ Batch jobs opérationnels

---

### Sprint 6 : Internationalisation et Docker

**Objectif** : i18n FR/EN et déploiement Docker.

#### Frontend
1. **i18n**
   - [ ] Bibliothèque i18n (react-i18next)
   - [ ] Fichiers traductions FR/EN (JSON)
   - [ ] Switch langue dans UI
   - [ ] Traduction composants wizard

#### Infrastructure
1. **Docker**
   - [ ] Dockerfile backend (Flask + Gunicorn)
   - [ ] Dockerfile frontend (React build + Nginx)
   - [ ] docker-compose.yml (frontend, backend, MySQL)
   - [ ] Variables d'environnement (.env)
   - [ ] Health checks services
   - [ ] Volumes persistants (MySQL, releases, uploads, logs)

2. **Déploiement**
   - [ ] Scripts migration DB dans Docker
   - [ ] Documentation déploiement
   - [ ] Checklist déploiement

#### Tests
- [ ] Tests i18n (switch langue)
- [ ] Tests Docker Compose (build + run)

**Critères d'acceptation** :
- ✅ Application traduite FR/EN
- ✅ Docker Compose fonctionnel
- ✅ Services démarrés correctement

---

### Sprint 7 : Tests E2E et Documentation

**Objectif** : Tests complets et documentation finale.

#### Tests
1. **E2E Web**
   - [ ] Scénario wizard complet (upload → packaging → téléchargement)
   - [ ] Scénario authentification (login → accès protégé → logout)
   - [ ] Scénario configuration (APIs, FTP)

2. **E2E CLI**
   - [ ] Scénario pack complet (`packer pack --interactive`)
   - [ ] Scénario batch jobs (`packer jobs list/show/logs`)

3. **Mocks**
   - [ ] Mocks APIs externes (OMDb, TVDB, OpenLibrary)
   - [ ] Mock MediaInfo
   - [ ] Mock FTP/SFTP

#### Documentation
- [ ] README complet (installation, utilisation, configuration)
- [ ] Documentation API (endpoints, schémas)
- [ ] Documentation CLI (commandes, exemples)
- [ ] Guide développement (setup, architecture)
- [ ] Guide déploiement Docker

**Critères d'acceptation** :
- ✅ Tests E2E passent tous
- ✅ Documentation complète et à jour

---

### Sprint 8 : Support DOCS et Optimisations

**Objectif** : Support règles DOCS et optimisations finales.

#### Backend
1. **Support DOCS**
   - [ ] Règles DOCS Scene (scraping + cache)
   - [ ] Packaging DOCS (adaptation règles)
   - [ ] Extraction métadonnées DOCS

2. **Optimisations**
   - [ ] Cache résultats APIs (TTL configurable)
   - [ ] Optimisation requêtes DB (index, pagination)
   - [ ] Optimisation packaging (parallélisation si possible)

#### Tests
- [ ] Tests support DOCS
- [ ] Tests performance (charges)

**Critères d'acceptation** :
- ✅ Support DOCS fonctionnel
- ✅ Performances satisfaisantes

---

## Dépendances Techniques à Ajouter

### Backend (requirements.txt)
```txt
# Authentification
flask-jwt-extended>=4.5.0

# Base de données
flask-sqlalchemy>=3.0.0
flask-migrate>=4.0.0
mysqlclient>=2.2.0  # ou pymysql>=1.1.0

# Chiffrement
cryptography>=41.0.0

# FTP/SFTP
paramiko>=3.3.0

# MediaInfo (optionnel)
pymediainfo>=6.0.0  # Si disponible, sinon CLI
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.16.0",
    "react-dropzone": "^14.2.0",
    "react-i18next": "^13.0.0",
    "bootstrap": "^5.3.0",
    "axios": "^1.5.0"
  }
}
```

---

## Notes d'Implémentation

### Architecture
- **Backend** : Garder structure modulaire existante (blueprints)
- **Frontend** : Nouveau projet React séparé, ou intégré Flask (selon préférence)
- **DB** : MySQL avec migrations Flask-Migrate
- **Auth** : JWT tokens avec refresh si nécessaire

### Sécurité
- **Chiffrement** : AES-GCM pour credentials (clé dérivée ou env)
- **Validation** : Marshmallow schemas (déjà en place)
- **Commandes** : Aucune validation/quoting (usage interne uniquement)

### Performance
- **Cache** : Flask-Caching pour APIs externes
- **DB** : Index sur clés métiers (user_id, job_id, etc.)
- **Packaging** : Synchrone simple (pas de queue async pour MVP)

### Tests
- **Unitaires** : pytest (déjà configuré)
- **Intégration** : Tests avec DB de test
- **E2E** : Playwright ou Cypress pour Web, pytest pour CLI

