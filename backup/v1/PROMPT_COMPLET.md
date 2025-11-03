# 🚀 MODE AUTONOME - TRAVAIL SANS INTERRUPTION

## INSTRUCTIONS PRINCIPALES

Travaille de manière autonome et continue sans demander de validation à chaque étape. Avance un maximum avant de revenir vers moi. Prends des décisions techniques appropriées et itère sur les améliorations.

## LOGGING ET DOCUMENTATION

- Tient un journal de progression (LOG & DIARY) au fil de l'avancement
- Documente chaque itération et amélioration dans `ITERATION_LOG.md`
- Compare les résultats avec les fichiers de contexte existants
- Effectue au minimum 4 itérations successives, chacune s'améliorant sur la précédente
- Crée un fichier `RMD` (Release Management Document) pour suivre les changements

## PRINCIPE

```
Continue sans me demander, car tu sembles très bien gérer la situation actuelle. 

Avance un maximum avant de revenir vers moi pour me demander de continuer ou 

d'apporter des modifications. Je suis sûr que tu es capable de prendre les 

bonnes décisions et de progresser efficacement dans ce que tu as à faire. 

Je te fais confiance pour aller de l'avant sans hésitation.
```

---

## 🧪 MÉTHODOLOGIE TDD (TEST DRIVEN DEVELOPMENT)

**RÈGLE FONDAMENTALE :**

Nous utiliserons une méthodologie TDD (Test Driven Development).

**PROCESSUS :**

1. **RED** : Écris d'abord les tests pour la fonctionnalité (même s'ils échouent)
2. **GREEN** : Implémente le minimum nécessaire pour faire passer les tests
3. **REFACTOR** : Améliore le code tout en maintenant les tests verts

**EXIGENCES :**

- Crée les tests AVANT d'implémenter toute nouvelle fonctionnalité
- Utilise pytest pour les tests Python
- Utilise Playwright MCP pour les tests E2E (simulation utilisateur)
- Assure-toi que tous les tests passent avant de continuer
- Mainten une couverture de tests > 80% pour le code critique
- Documente les cas de test dans les docstrings

---

## 📋 PHASE 0 : TESTS END-TO-END COMPLETS (SIMULATION UTILISATEUR)

**PRÉREQUIS :**

1. **Lancer l'interface web Flask avant tous les tests**
   - Script : `./start_server.sh` ou `python web/app.py`
   - Vérifier que le serveur est accessible sur `http://localhost:5000`

2. **Utiliser les MCP tools (Playwright) pour tester toutes les étapes**

**TESTS À EFFECTUER (via MCP Playwright) :**

- ✅ Authentification (login/logout) - **À VALIDER VIA MCP**
- ✅ Gestion utilisateurs/rôles (page admin `/users`) - **À VALIDER VIA MCP**
- ✅ Dashboard (résumés et statistiques) - **À VALIDER VIA MCP**
- ✅ Création de releases (EBOOK, TV) - **À VALIDER VIA MCP**
- ✅ Liste des releases et historique - **À VALIDER VIA MCP**
- ✅ Configuration des préférences - **À VALIDER VIA MCP**
- ✅ Configuration chemins par groupe/type - **À VALIDER VIA MCP**
- ✅ Configuration destinations FTP/SFTP - **À VALIDER VIA MCP**
- ✅ Tous les endpoints API existants - **À VALIDER VIA MCP**

**OBJECTIF :** Valider que chaque fonctionnalité existante fonctionne à 100% avant d'ajouter de nouvelles fonctionnalités.

**MÉTHODE :**
- Utiliser Playwright MCP pour simuler un utilisateur réel
- Tester chaque parcours utilisateur complet
- Documenter les résultats dans `TEST_E2E_RESULTS.md`

---

## ✅ DÉJÀ RÉALISÉ (À NE PAS REFAIRE)

**Infrastructure :**
- ✅ Base de données MySQL + SQLAlchemy (8 modèles complets)
- ✅ Authentification JWT backend + frontend
- ✅ Système de jobs avec logs et artefacts
- ✅ CLI enrichi (pack, batch, list-jobs, logs, prefs, templates)
- ✅ Préférences utilisateur/globales avec fallback
- ✅ Gestion chemins par groupe/type (`/api/paths`)
- ✅ Gestion destinations FTP/SFTP CRUD (`/api/destinations`)
- ✅ Modèle `ApiConfig` avec chiffrement

**Interface Web :**
- ✅ Page d'accueil accessible sans authentification
- ✅ Page de login fonctionnelle
- ✅ Dashboard avec statistiques (utilisateurs, jobs, releases)
- ✅ Page gestion utilisateurs/rôles (`/users` - admin uniquement)
- ✅ Système de déconnexion fonctionnel
- ✅ Menu utilisateur avec rôle admin visible

**Packaging :**
- ✅ Packaging EBOOK (conforme 2022)
- ✅ Packaging TV
- ✅ Extraction métadonnées EPUB/PDF/MOBI
- ✅ MediaInfo intégration pour TV (fonction `probe_media_info` existe)

**APIs Enrichissement :**
- ✅ OpenLibrary (eBooks)
- ✅ Google Books (eBooks)

**Templates :**
- ✅ CRUD templates NFO (`/api/templates`)
- ✅ Service `TemplateRenderer` avec placeholders

---

## 🔨 PRIORITÉ HAUTE - CRITIQUES

### 1. Upload FTP/SFTP Automatique (0%)

**État actuel :**
- ✅ Modèle `Destination` existe (`web/models/destination.py`)
- ✅ CRUD destinations existe (`web/blueprints/destinations.py`)
- ✅ Chiffrement mots de passe implémenté
- ✅ `paramiko>=3.3.0` dans requirements.txt
- ❌ **Service upload FTP/SFTP MANQUANT**
- ❌ **Intégration dans PackagingService MANQUANTE**
- ❌ **Support multi-volumes (ZIP/RAR) MANQUANT**
- ❌ **Endpoints export manuels MANQUANTS**

**À faire :**

1. **Service Upload FTP/SFTP** (`web/services/ftp_upload.py`) :
   ```python
   class FtpUploadService:
       def upload_to_ftp(destination_id: int, files: List[Path], job_id: Optional[str] = None) -> Tuple[bool, str]
       def upload_to_sftp(destination_id: int, files: List[Path], job_id: Optional[str] = None) -> Tuple[bool, str]
       def test_connection(destination_id: int) -> Tuple[bool, str]
   ```
   - Support FTP (`ftplib`) et SFTP (`paramiko`)
   - Gestion multi-volumes (ZIP/RAR) : uploader tous les volumes séquentiellement
   - Retry avec backoff exponentiel (3 tentatives max, délais : 1s, 2s, 4s)
   - Logs dans `job_logs` avec `job_id` si fourni
   - Timeout configurable (défaut 30s pour FTP, 60s pour SFTP)
   - Vérification existence fichiers avant upload
   - Création répertoires distants si nécessaire
   - Support chemin distant personnalisé (`Destination.path`)

2. **Intégration dans PackagingService** (`web/services/packaging.py`) :
   - Modifier `PackagingService.pack_ebook()` et `pack_tv()`
   - Après `job.complete()`, vérifier si `export_config` contient destination FTP/SFTP
   - Si oui :
     - Récupérer destination par `destination_id` ou `group_name`
     - Collecter tous les artefacts (ZIP, RAR volumes, NFO, DIZ, SFV)
     - Appeler `FtpUploadService.upload_to_ftp()` ou `upload_to_sftp()`
     - Logger progression dans `job_logs` (INFO/ERROR)
     - Gérer erreurs : log ERROR mais ne pas faire échouer le job

3. **Endpoints API Export** (`web/blueprints/jobs.py`) :
   - `POST /api/jobs/<job_id>/export/ftp` : Upload manuel FTP
     - Body: `{"destination_id": 1}` ou `{"destination_name": "..."}`
   - `POST /api/jobs/<job_id>/export/sftp` : Upload manuel SFTP
   - `POST /api/destinations/<destination_id>/test` : Test connexion

4. **Intégration dans Wizard** :
   - Modifier `web/blueprints/wizard.py` :
     - Dans `pack()`, après création job, vérifier `export_config`
     - Si FTP/SFTP configuré, lancer upload automatique

5. **Support RAR Multi-Volumes** :
   - Détecter volumes RAR : `.r00`, `.r01`, `.r02`, etc.
   - Uploader dans l'ordre (`.rar` puis `.r00`, `.r01`, etc.)
   - Vérifier intégrité (optionnel : vérifier CRC32 si disponible)

**Tests :**
- Tests unitaires service FTP/SFTP (mocks `ftplib`/`paramiko`)
- Tests intégration avec serveur FTP/SFTP de test (Docker container)
- Tests E2E via Playwright (création release + upload automatique)
- Tests gestion erreurs (timeout, connexion refusée, authentification échouée)

---

### 2. Intégrations APIs TV - OMDb/TVDB/TMDb (0%)

**État actuel :**
- ✅ Modèle `ApiConfig` existe (`web/models/api_config.py`)
- ✅ Chiffrement clés API implémenté
- ✅ OpenLibrary/Google Books existent (`src/metadata/api_enricher.py`)
- ❌ **Service APIs TV MANQUANT**
- ❌ **Blueprint API Config MANQUANT**
- ❌ **Intégration dans enrichissement métadonnées TV MANQUANTE**
- ❌ **Authentification TVDB JWT avec refresh MANQUANTE**

**À faire :**

1. **Service APIs TV** (`src/metadata/tv_apis.py`) :
   ```python
   class TvApiEnricher:
       def enrich_from_omdb(title: str, season: Optional[int] = None, episode: Optional[int] = None, api_key: str) -> Dict[str, Any]
       def enrich_from_tvdb(title: str, season: Optional[int] = None, episode: Optional[int] = None, api_key: str, user_key: str) -> Dict[str, Any]
       def enrich_from_tmdb(title: str, season: Optional[int] = None, episode: Optional[int] = None, api_key: str) -> Dict[str, Any]
       def enrich(title: str, season: Optional[int] = None, episode: Optional[int] = None, config: Optional[Dict] = None) -> Dict[str, Any]
   ```
   - Priorité fusion : TVDB > TMDb > OMDb
   - Retry avec backoff (3 tentatives, délais : 1s, 2s, 4s)
   - Timeout configurable (défaut 10s)
   - Gestion quotas/rate limiting
   - Cache résultats (Flask-Caching, TTL 24h)

2. **Authentification TVDB JWT** (`src/metadata/tvdb_auth.py`) :
   ```python
   class TvdbAuthenticator:
       def __init__(self, api_key: str, user_key: str, username: str)
       def get_token() -> str  # Récupère token (cache ou refresh)
       def refresh_token() -> str  # Force refresh
   ```
   - JWT avec refresh automatique
   - Cache token (TTL 30 jours, stocké en mémoire ou Redis)
   - Gestion expiration et renouvellement automatique
   - Retry si 401 (token expiré)

3. **Fusion Métadonnées TV** :
   - Étendre `MetadataEnricher` ou créer `TvMetadataEnricher`
   - Fusion MediaInfo (existant `probe_media_info`) + APIs TV
   - Priorité : TVDB > TMDb > OMDb > MediaInfo local

4. **Blueprint API Config** (`web/blueprints/api_config.py`) :
   ```python
   @api_config_bp.get('/apis')  # Liste configs APIs (admin/self)
   @api_config_bp.post('/apis')  # Créer config API
   @api_config_bp.get('/apis/<api_name>')  # Récupérer config
   @api_config_bp.put('/apis/<api_name>')  # Mettre à jour
   @api_config_bp.delete('/apis/<api_name>')  # Supprimer
   @api_config_bp.post('/apis/<api_name>/test')  # Tester connexion API
   ```
   - Protection admin uniquement (sauf GET pour own user)
   - Validation schémas Marshmallow
   - Support : `omdb`, `tvdb`, `tmdb`, `openlibrary`

5. **Intégration dans Wizard** (`web/blueprints/wizard.py`) :
   - Dans `pack()`, si type TV et `use_apis=True` :
     - Charger configs APIs depuis `ApiConfig` (user ou global)
     - Appeler `TvApiEnricher.enrich()` avec configs
     - Fusionner résultats avec MediaInfo

6. **Intégration dans PackagingService** (`web/services/packaging.py`) :
   - Modifier `pack_tv()` pour utiliser APIs TV si configurées

**Tests :**
- Tests unitaires avec mocks APIs TV (réponses JSON simulées)
- Tests authentification TVDB (mock JWT)
- Tests fusion métadonnées (TVDB + TMDb + OMDb)
- Tests gestion quotas/rate limiting
- Tests cache (vérifier TTL)

---

### 3. Packaging Type DOCS (0%)

**État actuel :**
- ✅ Type DOCS défini dans schémas (`WizardPackRequestSchema.type`)
- ✅ Modèle `Job.type` supporte 'DOCS'
- ✅ Validation dans wizard backend (`if release_type not in ['TV', 'EBOOK', 'DOCS']`)
- ✅ Mentionné dans `template_renderer.py`
- ❌ **Fonction packaging DOCS MANQUANTE**
- ❌ **Extraction métadonnées DOCS MANQUANTE**
- ❌ **Support CLI DOCS MANQUANT**

**À faire :**

1. **Service Packaging DOCS** (`src/packaging/docs_packer.py`) :
   ```python
   def pack_docs_release(
       docs_path: str | Path,
       group: str,
       output_dir: Optional[str | Path] = None,
       source_type: Optional[str] = None,
       url: Optional[str] = None,
       enable_api: bool = True,
       nfo_template_path: Optional[str | Path] = None,
       config: Optional[Dict[str, Any]] = None,
   ) -> str
   ```
   - Support formats : PDF, DOCX, TXT, ODT, RTF
   - Extraction métadonnées documents
   - Génération nom release conforme Scene DOCS
   - Packaging ZIP/RAR multi-volumes (même règles que EBOOK)
   - Génération NFO DOCS (template adapté)
   - Génération SFV/DIZ

2. **Extraction Métadonnées DOCS** (`src/metadata/docs.py`) :
   ```python
   def extract_pdf_metadata(filepath: Path) -> Dict[str, Optional[str]]  # Déjà existe, vérifier si complet
   def extract_docx_metadata(filepath: Path) -> Dict[str, Optional[str]]
   def extract_txt_metadata(filepath: Path) -> Dict[str, Optional[str]]
   def extract_odt_metadata(filepath: Path) -> Dict[str, Optional[str]]
   def extract_rtf_metadata(filepath: Path) -> Dict[str, Optional[str]]
   ```
   - PDF : Utiliser `PyPDF2` (déjà dans requirements)
   - DOCX : Utiliser `python-docx` (à ajouter dans requirements)
   - TXT/ODT/RTF : Parsing basique (metadata minimale)
   - Enrichissement via APIs si disponibles (ex: ISBN lookup)

3. **Intégration PackagingService** (`web/services/packaging.py`) :
   - Méthode `PackagingService.pack_docs()` :
     ```python
     def pack_docs(
         self,
         docs_path: str | Path,
         group: str,
         output_dir: Optional[str | Path] = None,
         source_type: Optional[str] = None,
         url: Optional[str] = None,
         enable_api: bool = True,
         nfo_template_path: Optional[str | Path] = None,
         config: Optional[Dict[str, Any]] = None,
     ) -> Job
     ```

4. **Intégration dans Wizard** (`web/blueprints/wizard.py`) :
   - Dans `pack()`, ajouter cas `elif job_type == 'DOCS'` :
     - Extraction métadonnées DOCS
     - Appel `packaging_service.pack_docs()`

5. **Support CLI** (`src/packer_cli.py`) :
   - Dans `pack_command()`, ajouter support `--type DOCS`
   - Utiliser `pack_docs_release()` directement

6. **Templates NFO DOCS** :
   - Vérifier que `template_renderer.py` supporte type DOCS
   - Template spécifique DOCS (placeholders : auteur, éditeur, ISBN, date publication, etc.)

7. **Dépendances** :
   - Ajouter `python-docx>=1.1.0` dans `requirements.txt`

**Tests :**
- Tests unitaires extraction métadonnées DOCS (tous formats)
- Tests packaging DOCS complet (PDF, DOCX)
- Tests conformité Scene Rules DOCS
- Tests E2E via Playwright (création release DOCS)

---

### 4. Blueprint API Config Manquant (0%)

**État actuel :**
- ✅ Modèle `ApiConfig` existe (`web/models/api_config.py`)
- ✅ Chiffrement implémenté
- ❌ **Blueprint API Config MANQUANT**
- ❌ **Endpoints `/api/config/apis` MANQUANTS**
- ❌ **Interface frontend configuration APIs MANQUANTE**

**À faire :**

1. **Blueprint API Config** (`web/blueprints/api_config.py`) :
   ```python
   api_config_bp = Blueprint('api_config', __name__)
   
   @api_config_bp.get('/apis')
   @jwt_required()
   @operator_or_admin_required
   def list_api_configs()
   
   @api_config_bp.post('/apis')
   @jwt_required()
   @operator_or_admin_required
   def create_api_config()
   
   @api_config_bp.get('/apis/<api_name>')
   @jwt_required()
   @operator_or_admin_required
   def get_api_config(api_name: str)
   
   @api_config_bp.put('/apis/<api_name>')
   @jwt_required()
   @operator_or_admin_required
   def update_api_config(api_name: str)
   
   @api_config_bp.delete('/apis/<api_name>')
   @jwt_required()
   @admin_required
   def delete_api_config(api_name: str)
   
   @api_config_bp.post('/apis/<api_name>/test')
   @jwt_required()
   @operator_or_admin_required
   def test_api_connection(api_name: str)
   ```
   - Protection : admin pour toutes, ou user pour ses propres configs
   - Support : `omdb`, `tvdb`, `tmdb`, `openlibrary`
   - Validation schémas Marshmallow
   - Ne jamais retourner clés API en clair (sauf pour test avec masquage)

2. **Schémas Marshmallow** (`web/schemas/api_config.py`) :
   ```python
   class ApiConfigSchema(Schema)
   class ApiConfigCreateSchema(Schema)
   class ApiConfigUpdateSchema(Schema)
   ```

3. **Enregistrement dans app.py** :
   - `from web.blueprints.api_config import api_config_bp`
   - `app.register_blueprint(api_config_bp, url_prefix='/api/config')`

4. **Interface Frontend** :
   - Page `/config/apis` ou modal dans dashboard
   - Formulaire saisie clés API (OMDb, TVDB, TMDb, OpenLibrary)
   - Liste configurations existantes
   - Bouton test connexion pour chaque API
   - Masquage clés API (affichage `***` sauf au moment saisie)

**Tests :**
- Tests unitaires CRUD API configs
- Tests chiffrement/déchiffrement
- Tests protection admin/user
- Tests E2E via Playwright (création/modification config API)

---

### 5. Tests E2E Complets avec Playwright MCP (0%)

**État actuel :**
- ✅ Infrastructure Playwright MCP configurée (`.cursor/mcp.example.json`)
- ✅ Tests unitaires existent (`tests/`)
- ❌ **Dossier `tests/e2e/` MANQUANT**
- ❌ **Tests Playwright E2E MANQUANTS**

**À faire :**

1. **Structure Tests E2E** :
   ```
   tests/e2e/
   ├── __init__.py
   ├── conftest.py  # Fixtures serveur Flask + DB test
   ├── test_wizard_flow.py  # Scénario wizard complet
   ├── test_auth_flow.py  # Scénario authentification
   ├── test_users_management.py  # Scénario gestion utilisateurs
   ├── test_configuration.py  # Scénario configuration (préférences, chemins, destinations)
   ├── test_ftp_upload.py  # Scénario upload FTP/SFTP
   └── fixtures/
       ├── test_ebook.pdf
       └── test_video.mkv
   ```

2. **Fixtures Serveur Flask** (`tests/e2e/conftest.py`) :
   ```python
   @pytest.fixture(scope="session")
   def flask_server():
       # Démarrer serveur Flask dans thread séparé
       # Port 5000 ou port aléatoire
       # Nettoyage après tests
   ```

3. **Tests Wizard Flow** (`tests/e2e/test_wizard_flow.py`) :
   - Scénario complet : login → wizard → upload fichier → packaging → résultats
   - Tests pour chaque type (EBOOK, TV, DOCS)
   - Validation prévisualisation NFO
   - Validation arborescence release

4. **Tests Authentification** (`tests/e2e/test_auth_flow.py`) :
   - Login avec credentials valides/invalides
   - Redirection automatique si non authentifié
   - Logout et nettoyage token

5. **Tests Gestion Utilisateurs** (`tests/e2e/test_users_management.py`) :
   - Création utilisateur (admin)
   - Modification utilisateur
   - Suppression utilisateur
   - Protection admin uniquement

6. **Tests Configuration** (`tests/e2e/test_configuration.py`) :
   - Configuration préférences
   - Configuration chemins par groupe/type
   - Configuration destinations FTP/SFTP
   - Configuration APIs

7. **Tests FTP Upload** (`tests/e2e/test_ftp_upload.py`) :
   - Upload automatique après packaging
   - Upload manuel via endpoint
   - Test connexion FTP/SFTP

8. **Utilisation Playwright MCP** :
   - Utiliser `@browserbasehq/mcp-playwright` pour tests
   - Automatiser lancement serveur avant tests
   - Screenshots en cas d'échec
   - Documentation utilisation MCP tools

**Tests :**
- Tous les scénarios E2E doivent passer
- Couverture > 80% pour parcours critiques
- Documentation dans `TEST_E2E_RESULTS.md`

---

## 🔶 PRIORITÉ MOYENNE - IMPORTANTES

### 6. Docker Compose (0%)

**À faire :**

1. **Dockerfile Backend** (`Dockerfile`) :
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "web.app:create_app()"]
   ```

2. **docker-compose.yml** :
   ```yaml
   version: '3.8'
   services:
     mysql:
       image: mysql:8.0
       environment:
         MYSQL_DATABASE: packer
         MYSQL_USER: packer
         MYSQL_PASSWORD: packer
       volumes:
         - mysql_data:/var/lib/mysql
       ports:
         - "3306:3306"
     
     backend:
       build: .
       environment:
         DATABASE_URL: mysql+pymysql://packer:packer@mysql:3306/packer
         JWT_SECRET_KEY: ${JWT_SECRET_KEY}
         API_KEYS_ENCRYPTION_KEY: ${API_KEYS_ENCRYPTION_KEY}
       volumes:
         - ./releases:/app/releases
         - ./uploads:/app/uploads
         - ./logs:/app/logs
       ports:
         - "5000:5000"
       depends_on:
         - mysql
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   ```

3. **Documentation** (`DEPLOYMENT.md`) :
   - Instructions installation Docker
   - Variables d'environnement documentées (`.env.example`)
   - Scripts migration DB dans Docker
   - Health checks

4. **Scripts** :
   - `docker-compose up -d` : Démarrage services
   - `docker-compose exec backend python web/scripts/init_db.py` : Init DB
   - `docker-compose exec backend python web/scripts/seed_admin.py` : Admin

**Tests :**
- Tests build Docker
- Tests démarrage services
- Tests health checks

---

### 7. Wizard Frontend Complet (5%)

**État actuel :**
- ✅ Wizard backend complet (12 étapes validées)
- ✅ Schémas Marshmallow complets
- ❌ **Wizard frontend MANQUANT** (`web/static/js/wizard.js` est presque vide)

**À faire :**

1. **Wizard Frontend** (`web/static/js/wizard.js`) :
   - 12 étapes complètes avec validation
   - Navigation forward/backward
   - État global wizard (localStorage ou sessionStorage)
   - Prévisualisation NFO en temps réel
   - Arborescence release générée
   - Gestion erreurs et retry
   - Loaders et indicateurs progression

2. **Composants Wizard** (à créer dans `web/templates/` ou JS modulaire) :
   - Step 1 : Nom groupe
   - Step 2 : Type release (TV/EBOOK/DOCS)
   - Step 3 : Règles Scene (multi-sélection)
   - Step 4 : Fichiers (upload drag & drop + URL distant)
   - Step 5 : Métadonnées (formulaire + extraction auto)
   - Step 6 : Enrichissement (MediaInfo, APIs)
   - Step 7 : Template NFO (sélection + prévisualisation)
   - Step 8 : Résumé (édition manuelle)
   - Step 9 : Export (download, FTP/SFTP)
   - Step 10 : Résultats (arborescence, téléchargement)

3. **Prévisualisation NFO** :
   - Appel API `/api/templates/<template_id>/render` avec données de test
   - Affichage NFO rendu en temps réel (textarea ou div monospace)
   - Validation ASCII/UTF-8

4. **Arborescence Release** :
   - Appel API `/api/jobs/<job_id>/artifacts`
   - Affichage arborescence fichiers (tree view)
   - Téléchargement fichiers individuels

**Tests :**
- Tests E2E wizard complet via Playwright
- Tests validation étapes frontend
- Tests prévisualisation NFO

---

### 8. Interface Configuration APIs/FTP (0%)

**À faire :**

1. **Page Configuration** (`web/templates/config.html`) :
   - Onglets : APIs, Destinations FTP/SFTP, Chemins
   - Formulaire saisie clés API
   - Liste destinations FTP/SFTP
   - Test connexion pour chaque API/FTP

2. **JavaScript** (`web/static/js/config.js`) :
   - CRUD APIs configs
   - CRUD destinations FTP/SFTP
   - Test connexion APIs/FTP
   - Masquage clés API/mots de passe

**Tests :**
- Tests E2E configuration via Playwright

---

### 9. Endpoints Manquants**

1. **Endpoint Test Connexion FTP/SFTP** :
   - `POST /api/destinations/<destination_id>/test`
   - Retourne `{"success": bool, "message": str}`

2. **Endpoint Export Métadonnées JSON** :
   - `GET /api/jobs/<job_id>/metadata`
   - Retourne métadonnées format JSON standardisé

3. **Endpoint Enrichissement Métadonnées** :
   - `POST /api/metadata/enrich`
   - Body: `{"metadata": {...}, "type": "TV|EBOOK", "config": {...}}`
   - Retourne métadonnées enrichies

---

## 🔷 PRIORITÉ BASSE - BONUS

### 10. Internationalisation FR/EN (0%)

**À faire :**
- Flask-Babel backend
- Système i18n frontend (JavaScript)
- Fichiers traductions FR/EN (`translations/fr.json`, `translations/en.json`)
- Switch langue dans UI

---

### 11. Thumbnails Vidéo (0%)

**À faire :**
- Service extraction frames avec `ffmpeg`
- Génération thumbnails pour releases TV
- Stockage thumbnails (local ou CDN)
- Endpoint `/api/jobs/<job_id>/thumbnail`

---

### 12. Rétention et Nettoyage (0%)

**À faire :**
- Service nettoyage automatique (`web/services/cleanup.py`)
- Tâche planifiée (cron ou Celery)
- Configuration rétention (jours) dans préférences globales
- Nettoyage jobs anciens, releases orphelines, logs anciens

---

## 📝 ORDRE D'EXÉCUTION RECOMMANDÉ

1. **Phase 0 - Tests E2E** : Valider toutes les fonctionnalités existantes à 100% avec Playwright MCP
2. **Priorité Haute 1 - Upload FTP/SFTP** : Implémenter service upload automatique
3. **Priorité Haute 2 - Blueprint API Config** : Créer endpoints configuration APIs
4. **Priorité Haute 3 - APIs TV** : Intégrer OMDb/TVDB/TMDb
5. **Priorité Haute 4 - Packaging DOCS** : Implémenter fonction `pack_docs_release()`
6. **Priorité Moyenne 1 - Docker Compose** : Configuration déploiement
7. **Priorité Moyenne 2 - Tests E2E Complets** : Suite tests Playwright
8. **Priorité Moyenne 3 - Wizard Frontend** : Interface wizard complète
9. **Priorité Moyenne 4 - Interface Configuration** : Pages configuration APIs/FTP
10. **Documentation** : Maintenir à jour les fichiers de documentation et de log

---

## 📊 ESTIMATION EFFORT

- **Priorité Haute** : ~10-12 jours
  - Upload FTP/SFTP : ~3-4j
  - Blueprint API Config : ~1j
  - APIs TV : ~3-4j
  - Packaging DOCS : ~2-3j

- **Priorité Moyenne** : ~10-12 jours
  - Docker Compose : ~1-2j
  - Tests E2E : ~3-4j
  - Wizard Frontend : ~4-5j
  - Interface Configuration : ~2j

- **Priorité Basse** : ~5 jours

**Total estimé** : ~25-29 jours

---

## 🎯 RÉSUMÉ DES ACTIONS PRIORITAIRES

1. ✅ **Tester l'existant (Phase 0)** : Valider toutes les fonctionnalités avec Playwright MCP
2. 📤 **Upload FTP/SFTP automatique** : Service upload + intégration packaging
3. ⚙️ **Blueprint API Config** : Endpoints configuration APIs
4. 📺 **APIs TV (OMDb/TVDB/TMDb)** : Service enrichissement métadonnées TV
5. 📄 **Packaging DOCS** : Implémenter `pack_docs_release()`
6. 🐳 **Docker Compose** : Configuration déploiement complet
7. 🧪 **Tests E2E complets** : Suite tests Playwright pour tous parcours
8. 🌐 **Wizard frontend complet** : Interface wizard 12 étapes
9. 🔧 **Interface configuration** : Pages configuration APIs/FTP

---

## 📌 NOTES IMPORTANTES

- **Tests d'abord** : Toujours créer les tests avant l'implémentation (TDD)
- **MCP Tools** : Utiliser Playwright MCP pour tests E2E et validation
- **Autonomie** : Travailler sans interruption, itérer plusieurs fois avant de demander validation
- **Documentation** : Maintenir les logs de progression et la documentation à jour
- **Standards** : Respecter les règles Python et Bash définies ci-dessus
- **Qualité** : Maintenir une qualité de code élevée avec des tests complets
- **Serveur Flask** : Toujours démarrer le serveur avant les tests E2E
- **Sécurité** : Ne jamais exposer clés API/mots de passe en clair dans les réponses API

