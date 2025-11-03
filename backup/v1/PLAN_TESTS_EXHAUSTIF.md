# 🧪 PLAN DE TESTS EXHAUSTIF - Packer de Release

**Date** : 2025-01-27  
**Objectif** : Tests à 100% pour Docker, Interface Web, et Packaging de Release  
**Statut** : 📋 **PLAN COMPLET PRÊT POUR EXÉCUTION**

---

## 📊 RÉSUMÉ EXÉCUTIF

| Domaine | Tests Planifiés | Priorité | Durée Estimée |
|---------|----------------|----------|---------------|
| **Docker** | 85+ tests | 🔴 CRITIQUE | 4-6 heures |
| **Interface Web** | 120+ tests | 🔴 CRITIQUE | 6-8 heures |
| **Packaging Release** | 95+ tests | 🔴 CRITIQUE | 5-7 heures |
| **TOTAL** | **300+ tests** | - | **15-21 heures** |

---

## 🐳 PARTIE 1 : TESTS DOCKER À 100%

### 1.1 Tests d'Infrastructure Docker

#### 1.1.1 Vérification Prérequis
- [ ] **T01.001** : Docker installé et accessible (`docker --version`)
- [ ] **T01.002** : Docker Compose installé (`docker-compose --version`)
- [ ] **T01.003** : Docker daemon en cours d'exécution (`docker info`)
- [ ] **T01.004** : Espace disque suffisant (>10GB recommandé)
- [ ] **T01.005** : Ports 3306 et 5000 disponibles
- [ ] **T01.006** : Permissions Docker correctes (user dans groupe docker)

#### 1.1.2 Validation Dockerfile
- [ ] **T01.007** : Dockerfile syntaxiquement correct (`docker build --dry-run`)
- [ ] **T01.008** : Image basée sur Python 3.11-slim
- [ ] **T01.009** : Dépendances système installées (gcc, libmysqlclient-dev, mediainfo, rar)
- [ ] **T01.010** : Requirements.txt installé sans erreur
- [ ] **T01.011** : Application copiée correctement
- [ ] **T01.012** : Répertoires créés (/app/releases, /app/uploads, /app/logs)
- [ ] **T01.013** : Utilisateur non-root créé (appuser, UID 1000)
- [ ] **T01.014** : Permissions correctes sur /app
- [ ] **T01.015** : Port 5000 exposé
- [ ] **T01.016** : CMD Gunicorn correct avec 4 workers

#### 1.1.3 Build et Image
- [ ] **T01.017** : Build image réussit sans erreur
- [ ] **T01.018** : Image créée avec tag correct
- [ ] **T01.019** : Taille image raisonnable (<2GB recommandé)
- [ ] **T01.020** : Image ne contient pas de secrets hardcodés
- [ ] **T01.021** : Image scan sécurité (trivy/grype) - 0 vulnérabilités critiques

### 1.2 Tests Docker Compose

#### 1.2.1 Configuration Services
- [ ] **T01.022** : Fichier docker-compose.yml valide (syntaxe YAML)
- [ ] **T01.023** : Service MySQL défini avec image mysql:8.0
- [ ] **T01.024** : Service backend défini avec build context
- [ ] **T01.025** : Réseau packer_network créé (bridge)
- [ ] **T01.026** : Volumes définis (mysql_data, releases_data, uploads_data, logs_data)

#### 1.2.2 Service MySQL
- [ ] **T01.027** : MySQL démarre correctement
- [ ] **T01.028** : Variables d'environnement MySQL configurées
  - [ ] **T01.028.1** : MYSQL_ROOT_PASSWORD définie
  - [ ] **T01.028.2** : MYSQL_DATABASE définie (par défaut: packer)
  - [ ] **T01.028.3** : MYSQL_USER définie (par défaut: packer)
  - [ ] **T01.028.4** : MYSQL_PASSWORD définie
- [ ] **T01.029** : Port MySQL mappé (3306:3306)
- [ ] **T01.030** : Health check MySQL fonctionne (`mysqladmin ping`)
- [ ] **T01.031** : MySQL accessible depuis host (localhost:3306)
- [ ] **T01.032** : MySQL accessible depuis backend (mysql:3306)
- [ ] **T01.033** : Base de données créée automatiquement
- [ ] **T01.034** : Utilisateur créé avec permissions correctes
- [ ] **T01.035** : Volume mysql_data persiste les données
- [ ] **T01.036** : MySQL redémarre proprement après `docker-compose restart`

#### 1.2.3 Service Backend
- [ ] **T01.037** : Backend build réussi
- [ ] **T01.038** : Backend démarre correctement
- [ ] **T01.039** : Variables d'environnement backend configurées
  - [ ] **T01.039.1** : DATABASE_URL correcte (mysql+pymysql://...)
  - [ ] **T01.039.2** : JWT_SECRET_KEY définie
  - [ ] **T01.039.3** : API_KEYS_ENCRYPTION_KEY définie
  - [ ] **T01.039.4** : FLASK_ENV (production/development)
  - [ ] **T01.039.5** : RELEASES_FOLDER (/app/releases)
- [ ] **T01.040** : Port backend mappé (5000:5000 ou personnalisé)
- [ ] **T01.041** : Backend attend MySQL (depends_on avec condition)
- [ ] **T01.042** : Health check backend fonctionne (`/health`)
- [ ] **T01.043** : Backend accessible depuis host (http://localhost:5000)
- [ ] **T01.044** : Volumes montés correctement
  - [ ] **T01.044.1** : releases_data → /app/releases
  - [ ] **T01.044.2** : uploads_data → /app/uploads
  - [ ] **T01.044.3** : logs_data → /app/logs
- [ ] **T01.045** : Backend utilise utilisateur non-root (appuser)
- [ ] **T01.046** : Gunicorn démarre avec 4 workers
- [ ] **T01.047** : Logs backend accessibles (`docker-compose logs backend`)
- [ ] **T01.048** : Backend redémarre proprement après `docker-compose restart`

### 1.3 Tests d'Intégration Docker

#### 1.3.1 Connexion Backend → MySQL
- [ ] **T01.049** : Backend se connecte à MySQL au démarrage
- [ ] **T01.050** : Backend peut créer tables (init_db)
- [ ] **T01.051** : Backend peut lire/écrire dans base de données
- [ ] **T01.052** : Backend gère reconnexion après perte connexion MySQL
- [ ] **T01.053** : Backend gère timeout connexion MySQL (>30s)

#### 1.3.2 Persistance Données
- [ ] **T01.054** : Données MySQL persistées après `docker-compose down`
- [ ] **T01.055** : Releases persistées après redémarrage
- [ ] **T01.056** : Uploads persistés après redémarrage
- [ ] **T01.057** : Logs persistés après redémarrage
- [ ] **T01.058** : Volume mysql_data conserve données après suppression container

#### 1.3.3 Réseau Docker
- [ ] **T01.059** : Backend peut résoudre nom "mysql"
- [ ] **T01.060** : MySQL isolé (non accessible depuis extérieur sauf port)
- [ ] **T01.061** : Backend isolé dans réseau packer_network
- [ ] **T01.062** : Communication inter-services fonctionne

### 1.4 Tests de Performance Docker

- [ ] **T01.063** : Temps démarrage complet < 60 secondes
- [ ] **T01.064** : Utilisation mémoire MySQL < 512MB idle
- [ ] **T01.065** : Utilisation mémoire backend < 512MB idle
- [ ] **T01.066** : CPU usage < 10% idle (les deux services)
- [ ] **T01.067** : Latence connexion backend → MySQL < 5ms

### 1.5 Tests de Sécurité Docker

- [ ] **T01.068** : Pas de secrets dans docker-compose.yml
- [ ] **T01.069** : Variables d'environnement depuis .env
- [ ] **T01.070** : Utilisateur non-root dans container
- [ ] **T01.071** : Volumes avec permissions restrictives
- [ ] **T01.072** : Ports non exposés inutilement
- [ ] **T01.073** : Health checks configurés (prévention zombies)

### 1.6 Tests de Script start_docker.sh

- [ ] **T01.074** : Script exécutable (`chmod +x`)
- [ ] **T01.075** : Script détecte Docker manquant
- [ ] **T01.076** : Script détecte Docker Compose manquant
- [ ] **T01.077** : Script crée .env depuis .env.example si absent
- [ ] **T01.078** : Script démarre services Docker
- [ ] **T01.079** : Script attend MySQL ready
- [ ] **T01.080** : Script initialise base de données
- [ ] **T01.081** : Script crée utilisateur admin si absent
- [ ] **T01.082** : Script crée templates par défaut
- [ ] **T01.083** : Script vérifie health check backend
- [ ] **T01.084** : Script affiche URLs finales
- [ ] **T01.085** : Script gère erreurs proprement

### 1.7 Tests de Dépannage Docker

- [ ] **T01.086** : `docker-compose down` arrête tous services proprement
- [ ] **T01.087** : `docker-compose down -v` supprime volumes (avec confirmation)
- [ ] **T01.088** : `docker-compose restart backend` redémarre sans perte données
- [ ] **T01.089** : Logs accessibles en temps réel (`-f`)
- [ ] **T01.090** : Shell backend accessible (`docker-compose exec backend bash`)
- [ ] **T01.091** : Shell MySQL accessible (`docker-compose exec mysql bash`)

---

## 🌐 PARTIE 2 : TESTS INTERFACE WEB À 100%

### 2.1 Tests d'Infrastructure Web

#### 2.1.1 Accès et Routes
- [ ] **T02.001** : Serveur démarre sans erreur
- [ ] **T02.002** : Route `/` accessible (200 OK)
- [ ] **T02.003** : Route `/health` accessible (200 OK)
- [ ] **T02.004** : Route `/login` accessible (200 OK)
- [ ] **T02.005** : Route `/users` accessible (200 OK)
- [ ] **T02.006** : Route `/logout` redirige vers `/login`
- [ ] **T02.007** : Route inexistante retourne 404
- [ ] **T02.008** : Headers CORS corrects si configurés
- [ ] **T02.009** : Compression activée (gzip/brotli)

#### 2.1.2 Health Check
- [ ] **T02.010** : `/health` retourne JSON avec status
- [ ] **T02.011** : `/health` vérifie connexion MySQL
- [ ] **T02.012** : `/health` retourne "healthy" si tout OK
- [ ] **T02.013** : `/health` retourne "unhealthy" si MySQL down
- [ ] **T02.014** : `/health` temps réponse < 100ms

### 2.2 Tests d'Authentification

#### 2.2.1 Login
- [ ] **T02.015** : Page login affiche formulaire
- [ ] **T02.016** : Login avec credentials valides → succès + token
- [ ] **T02.017** : Login avec credentials invalides → erreur 401
- [ ] **T02.018** : Login avec username vide → erreur validation
- [ ] **T02.019** : Login avec password vide → erreur validation
- [ ] **T02.020** : Token JWT retourné après login
- [ ] **T02.021** : Token JWT contient user_id, username, role
- [ ] **T02.022** : Token JWT expire après délai configuré
- [ ] **T02.023** : Refresh token fonctionne

#### 2.2.2 Logout
- [ ] **T02.024** : Logout avec token valide → succès
- [ ] **T02.025** : Logout invalide token après logout
- [ ] **T02.026** : Logout redirige vers `/login`

#### 2.2.3 Protection Routes
- [ ] **T02.027** : Routes API protégées nécessitent token
- [ ] **T02.028** : Routes API sans token → 401 Unauthorized
- [ ] **T02.029** : Routes admin nécessitent rôle admin
- [ ] **T02.030** : Routes admin avec rôle operator → 403 Forbidden

### 2.3 Tests Dashboard

#### 2.3.1 Affichage
- [ ] **T02.031** : Dashboard accessible après login
- [ ] **T02.032** : Dashboard affiche statistiques utilisateurs
- [ ] **T02.033** : Dashboard affiche statistiques jobs
- [ ] **T02.034** : Dashboard affiche statistiques releases
- [ ] **T02.035** : Dashboard affiche graphiques/charts (si présents)
- [ ] **T02.036** : Dashboard mode public masque sections protégées
- [ ] **T02.037** : Dashboard mode admin affiche sections admin

#### 2.3.2 API Dashboard
- [ ] **T02.038** : `GET /api/dashboard/stats` retourne données
- [ ] **T02.039** : Stats contiennent nb_users, nb_jobs, nb_releases
- [ ] **T02.040** : Stats contiennent jobs par statut
- [ ] **T02.041** : Stats contiennent releases par type (EBOOK/TV/DOCS)

### 2.4 Tests Wizard de Packaging

#### 2.4.1 Navigation Wizard
- [ ] **T02.042** : Wizard accessible après login
- [ ] **T02.043** : Étape 1 : Sélection fichier fonctionne
- [ ] **T02.044** : Étape 2 : Sélection type release (EBOOK/TV/DOCS)
- [ ] **T02.045** : Étape 3 : Métadonnées affichées
- [ ] **T02.046** : Étape 4 : Configuration group
- [ ] **T02.047** : Étape 5 : Options source type (RETAIL/SCAN/HYBRID)
- [ ] **T02.048** : Étape 6 : URL optionnelle
- [ ] **T02.049** : Étape 7 : Template NFO sélection
- [ ] **T02.050** : Étape 8 : Prévisualisation configuration
- [ ] **T02.051** : Étape 9 : Confirmation
- [ ] **T02.052** : Bouton "Précédent" navigue vers étape précédente
- [ ] **T02.053** : Bouton "Suivant" valide avant navigation
- [ ] **T02.054** : Validation bloquante si champs requis manquants

#### 2.4.2 Upload Fichier
- [ ] **T02.055** : Upload eBook (EPUB) → succès
- [ ] **T02.056** : Upload eBook (MOBI) → succès
- [ ] **T02.057** : Upload eBook (PDF) → succès
- [ ] **T02.058** : Upload TV (MKV) → succès
- [ ] **T02.059** : Upload DOCS (PDF) → succès
- [ ] **T02.060** : Upload DOCS (DOCX) → succès
- [ ] **T02.061** : Upload fichier invalide → erreur
- [ ] **T02.062** : Upload fichier trop volumineux → erreur
- [ ] **T02.063** : Progress bar upload fonctionne

#### 2.4.3 Extraction Métadonnées
- [ ] **T02.064** : Métadonnées EPUB extraites correctement
- [ ] **T02.065** : Métadonnées MOBI extraites correctement
- [ ] **T02.066** : Métadonnées PDF extraites correctement
- [ ] **T02.067** : Métadonnées TV (MKV) extraites avec MediaInfo
- [ ] **T02.068** : Enrichissement API activable/désactivable
- [ ] **T02.069** : Métadonnées enrichies via Google Books (si activé)
- [ ] **T02.070** : Métadonnées enrichies via OpenLibrary (si activé)
- [ ] **T02.071** : Métadonnées enrichies via TVDB/OMDb/TMDb pour TV (si activé)

#### 2.4.4 Soumission Packaging
- [ ] **T02.072** : Soumission wizard crée job
- [ ] **T02.073** : Job retourné avec ID unique
- [ ] **T02.074** : Job status initial = "pending"
- [ ] **T02.075** : Redirection vers page jobs après soumission

### 2.5 Tests Gestion Jobs

#### 2.5.1 Liste Jobs
- [ ] **T02.076** : Page jobs accessible
- [ ] **T02.077** : Liste jobs affichée (table/liste)
- [ ] **T02.078** : Jobs triés par date (plus récent premier)
- [ ] **T02.079** : Filtre par statut fonctionne (pending/running/completed/failed)
- [ ] **T02.080** : Filtre par type fonctionne (EBOOK/TV/DOCS)
- [ ] **T02.081** : Recherche par nom release fonctionne
- [ ] **T02.082** : Pagination fonctionne (si >50 jobs)

#### 2.5.2 Détails Job
- [ ] **T02.083** : Détails job accessibles (modal/page)
- [ ] **T02.084** : Détails contiennent : ID, type, statut, dates, logs
- [ ] **T02.085** : Logs job affichés en temps réel
- [ ] **T02.086** : Artefacts job listés (fichiers générés)
- [ ] **T02.087** : Téléchargement artefacts fonctionne

#### 2.5.3 API Jobs
- [ ] **T02.088** : `GET /api/jobs` retourne liste jobs
- [ ] **T02.089** : `GET /api/jobs?status=completed` filtre par statut
- [ ] **T02.090** : `GET /api/jobs/{job_id}` retourne détails job
- [ ] **T02.091** : `GET /api/jobs/{job_id}/logs` retourne logs
- [ ] **T02.092** : `GET /api/jobs/{job_id}/artifacts` retourne artefacts
- [ ] **T02.093** : `DELETE /api/jobs/{job_id}` supprime job (si autorisé)

### 2.6 Tests Gestion Utilisateurs (Admin)

#### 2.6.1 Liste Utilisateurs
- [ ] **T02.094** : Page `/users` accessible (admin uniquement)
- [ ] **T02.095** : Liste utilisateurs affichée
- [ ] **T02.096** : Colonnes : username, email, role, created_at
- [ ] **T02.097** : Bouton "Créer utilisateur" visible (admin)

#### 2.6.2 Création Utilisateur
- [ ] **T02.098** : Formulaire création accessible
- [ ] **T02.099** : Création avec données valides → succès
- [ ] **T02.100** : Validation username (min 3 chars, alphanumeric)
- [ ] **T02.101** : Validation password (min 8 chars)
- [ ] **T02.102** : Validation email format
- [ ] **T02.103** : Création avec username existant → erreur
- [ ] **T02.104** : Création avec email existant → erreur

#### 2.6.3 Modification Utilisateur
- [ ] **T02.105** : Modification rôle utilisateur fonctionne
- [ ] **T02.106** : Modification email fonctionne
- [ ] **T02.107** : Modification password fonctionne
- [ ] **T02.108** : Auto-modification limitée (pas changer son propre rôle)

#### 2.6.4 Suppression Utilisateur
- [ ] **T02.109** : Suppression utilisateur fonctionne
- [ ] **T02.110** : Suppression utilisateur actuel → erreur
- [ ] **T02.111** : Suppression dernier admin → erreur

#### 2.6.5 API Utilisateurs
- [ ] **T02.112** : `GET /api/users` retourne liste utilisateurs
- [ ] **T02.113** : `POST /api/users` crée utilisateur
- [ ] **T02.114** : `PUT /api/users/{user_id}` modifie utilisateur
- [ ] **T02.115** : `DELETE /api/users/{user_id}` supprime utilisateur

### 2.7 Tests Préférences

#### 2.7.1 Affichage Préférences
- [ ] **T02.116** : Page préférences accessible
- [ ] **T02.117** : Préférences utilisateur affichées
- [ ] **T02.118** : Préférences globales affichées (admin)
- [ ] **T02.119** : Formulaire préférences pré-rempli avec valeurs actuelles

#### 2.7.2 Modification Préférences
- [ ] **T02.120** : Modification préférence utilisateur → sauvegarde
- [ ] **T02.121** : Modification préférence globale (admin) → sauvegarde
- [ ] **T02.122** : Fallback préférence globale si utilisateur non défini
- [ ] **T02.123** : Validation valeurs préférences

#### 2.7.3 API Préférences
- [ ] **T02.124** : `GET /api/preferences` retourne préférences
- [ ] **T02.125** : `PUT /api/preferences` sauvegarde préférences
- [ ] **T02.126** : `GET /api/preferences/global` retourne préférences globales (admin)
- [ ] **T02.127** : `PUT /api/preferences/global` sauvegarde globales (admin)

### 2.8 Tests Chemins (Paths)

#### 2.8.1 Gestion Chemins
- [ ] **T02.128** : Page chemins accessible
- [ ] **T02.129** : Liste chemins par groupe/type affichée
- [ ] **T02.130** : Création chemin fonctionne
- [ ] **T02.131** : Modification chemin fonctionne
- [ ] **T02.132** : Suppression chemin fonctionne
- [ ] **T02.133** : Validation chemin (existe, accessible en écriture)

#### 2.8.2 API Chemins
- [ ] **T02.134** : `GET /api/paths` retourne tous chemins
- [ ] **T02.135** : `GET /api/paths/{group}/{type}` retourne chemin spécifique
- [ ] **T02.136** : `POST /api/paths` crée chemin
- [ ] **T02.137** : `PUT /api/paths/{group}/{type}` modifie chemin
- [ ] **T02.138** : `DELETE /api/paths/{group}/{type}` supprime chemin

### 2.9 Tests Destinations FTP/SFTP

#### 2.9.1 Gestion Destinations
- [ ] **T02.139** : Page destinations accessible
- [ ] **T02.140** : Liste destinations affichée
- [ ] **T02.141** : Création destination FTP fonctionne
- [ ] **T02.142** : Création destination SFTP fonctionne
- [ ] **T02.143** : Test connexion destination fonctionne
- [ ] **T02.144** : Modification destination fonctionne
- [ ] **T02.145** : Suppression destination fonctionne

#### 2.9.2 API Destinations
- [ ] **T02.146** : `GET /api/destinations` retourne destinations
- [ ] **T02.147** : `POST /api/destinations` crée destination
- [ ] **T02.148** : `PUT /api/destinations/{dest_id}` modifie destination
- [ ] **T02.149** : `DELETE /api/destinations/{dest_id}` supprime destination
- [ ] **T02.150** : `POST /api/destinations/{dest_id}/test` teste connexion

### 2.10 Tests Templates NFO

#### 2.10.1 Gestion Templates
- [ ] **T02.151** : Modal/page templates accessible
- [ ] **T02.152** : Liste templates affichée
- [ ] **T02.153** : Prévisualisation template fonctionne
- [ ] **T02.154** : Création template fonctionne
- [ ] **T02.155** : Modification template fonctionne
- [ ] **T02.156** : Suppression template fonctionne (avec confirmation)
- [ ] **T02.157** : Sélection template "last used" fonctionne

#### 2.10.2 API Templates
- [ ] **T02.158** : `GET /api/templates` retourne templates
- [ ] **T02.159** : `POST /api/templates` crée template
- [ ] **T02.160** : `PUT /api/templates/{template_id}` modifie template
- [ ] **T02.161** : `DELETE /api/templates/{template_id}` supprime template
- [ ] **T02.162** : `POST /api/templates/{template_id}/preview` prévisualise template

### 2.11 Tests Releases

#### 2.11.1 Liste Releases
- [ ] **T02.163** : Page releases accessible
- [ ] **T02.164** : Liste releases affichée
- [ ] **T02.165** : Colonnes : nom, type, date, taille, artefacts
- [ ] **T02.166** : Filtre par type (EBOOK/TV/DOCS) fonctionne
- [ ] **T02.167** : Recherche par nom fonctionne
- [ ] **T02.168** : Tri par date/taille/nom fonctionne

#### 2.11.2 Détails Release
- [ ] **T02.169** : Détails release accessibles
- [ ] **T02.170** : Fichiers release listés (ZIP, RAR, NFO, DIZ, SFV)
- [ ] **T02.171** : Téléchargement NFO fonctionne
- [ ] **T02.172** : Téléchargement SFV fonctionne
- [ ] **T02.173** : Téléchargement ZIP/RAR fonctionne
- [ ] **T02.174** : Validation release conforme Scene Rules

### 2.12 Tests Responsive et UX

- [ ] **T02.175** : Interface responsive mobile (360px)
- [ ] **T02.176** : Interface responsive tablette (768px)
- [ ] **T02.177** : Interface responsive desktop (1280px+)
- [ ] **T02.178** : Navigation clavier complète (Tab, Enter, Esc)
- [ ] **T02.179** : Contraste WCAG 2.2 AA
- [ ] **T02.180** : Focus visible sur éléments interactifs
- [ ] **T02.181** : Messages d'erreur clairs et actionnables
- [ ] **T02.182** : Loaders non-bloquants
- [ ] **T02.183** : Dark mode fonctionne (si présent)

---

## 📦 PARTIE 3 : TESTS PACKAGING RELEASE À 100%

### 3.1 Tests Packaging EBOOK

#### 3.1.1 Formats Supportés
- [ ] **T03.001** : Packaging EPUB → succès
- [ ] **T03.002** : Packaging MOBI → succès
- [ ] **T03.003** : Packaging PDF → succès
- [ ] **T03.004** : Packaging AZW3 → succès
- [ ] **T03.005** : Packaging FB2 → succès
- [ ] **T03.006** : Packaging format non supporté → erreur

#### 3.1.2 Extraction Métadonnées EBOOK
- [ ] **T03.007** : Métadonnées EPUB extraites (title, author, isbn, etc.)
- [ ] **T03.008** : Métadonnées MOBI extraites correctement
- [ ] **T03.009** : Métadonnées PDF extraites correctement
- [ ] **T03.010** : Métadonnées manquantes gérées (valeurs par défaut)
- [ ] **T03.011** : ISBN valide formaté correctement
- [ ] **T03.012** : Date publication formatée correctement

#### 3.1.3 Génération Nom Release EBOOK
- [ ] **T03.013** : Nom release conforme format Scene Rules 2022
- [ ] **T03.014** : Nom release contient titre normalisé
- [ ] **T03.015** : Nom release contient auteur (si disponible)
- [ ] **T03.016** : Nom release contient année
- [ ] **T03.017** : Nom release contient format (EPUB/MOBI/PDF)
- [ ] **T03.018** : Nom release contient source type (RETAIL/SCAN/HYBRID)
- [ ] **T03.019** : Nom release contient langue
- [ ] **T03.020** : Nom release contient group tag
- [ ] **T03.021** : Nom release longueur < 255 caractères
- [ ] **T03.022** : Caractères spéciaux échappés/remplacés

#### 3.1.4 Structure Release EBOOK
- [ ] **T03.023** : Dossier release créé avec nom correct
- [ ] **T03.024** : eBook copié dans dossier release
- [ ] **T03.025** : Dossier Sample créé
- [ ] **T03.026** : Sample créé (premières pages)
- [ ] **T03.027** : Sample taille conforme (<10% original ou <50MB)

#### 3.1.5 Packaging ZIP Multi-volumes
- [ ] **T03.028** : ZIP créé avec méthode store (0)
- [ ] **T03.029** : ZIP volumes si taille > volume_size
- [ ] **T03.030** : ZIP volumes nommés correctement (vol01, vol02, ...)
- [ ] **T03.031** : ZIP volumes taille conforme (≈volume_size)
- [ ] **T03.032** : ZIP contient eBook original
- [ ] **T03.033** : ZIP contient Sample
- [ ] **T03.034** : ZIP CRC32 correct
- [ ] **T03.035** : ZIP décompressable sans erreur

#### 3.1.6 Packaging RAR (si configuré)
- [ ] **T03.036** : RAR créé si configuré (create_for_zip=True)
- [ ] **T03.037** : RAR volumes créés si taille > volume_size
- [ ] **T03.038** : RAR volumes nommés correctement (.part01.rar, ...)
- [ ] **T03.039** : RAR méthode store (0)
- [ ] **T03.040** : RAR décompressable sans erreur

#### 3.1.7 Génération NFO EBOOK
- [ ] **T03.041** : NFO généré avec template
- [ ] **T03.042** : NFO contient métadonnées correctes
- [ ] **T03.043** : NFO largeur ≤ 80 caractères (ASCII)
- [ ] **T03.044** : NFO ASCII art présent (si configuré)
- [ ] **T03.045** : NFO placeholders remplacés
- [ ] **T03.046** : NFO conditionnelles respectées
- [ ] **T03.047** : NFO nommé correctement (release_name.nfo)

#### 3.1.8 Génération DIZ
- [ ] **T03.048** : DIZ généré
- [ ] **T03.049** : DIZ contient informations release
- [ ] **T03.050** : DIZ largeur ≤ 44 caractères
- [ ] **T03.051** : DIZ lignes ≤ 30
- [ ] **T03.052** : DIZ nommé FILE_ID.DIZ

#### 3.1.9 Génération SFV
- [ ] **T03.053** : SFV généré
- [ ] **T03.054** : SFV contient tous fichiers release
- [ ] **T03.055** : SFV CRC32 correct pour chaque fichier
- [ ] **T03.056** : SFV format conforme (filename CRC32)
- [ ] **T03.057** : SFV nommé release_name.sfv

#### 3.1.10 Validation Release EBOOK
- [ ] **T03.058** : Validation release complète → succès
- [ ] **T03.059** : Validation détecte NFO manquant → erreur
- [ ] **T03.060** : Validation détecte SFV manquant → erreur
- [ ] **T03.061** : Validation détecte eBook manquant → erreur
- [ ] **T03.062** : Validation détecte format nom invalide → erreur

### 3.2 Tests Packaging TV

#### 3.2.1 Format Vidéo
- [ ] **T03.063** : Packaging MKV → succès
- [ ] **T03.064** : Packaging MP4 → succès (si supporté)
- [ ] **T03.065** : Format vidéo non supporté → erreur

#### 3.2.2 Extraction Métadonnées TV
- [ ] **T03.066** : MediaInfo extrait métadonnées vidéo
- [ ] **T03.067** : Métadonnées contiennent : résolution, codec, bitrate, fps
- [ ] **T03.068** : Métadonnées contiennent : durée, taille fichier
- [ ] **T03.069** : Enrichissement TVDB fonctionne (si activé)
- [ ] **T03.070** : Enrichissement TMDb fonctionne (si activé)
- [ ] **T03.071** : Enrichissement OMDb fonctionne (si activé)

#### 3.2.3 Génération Nom Release TV
- [ ] **T03.072** : Nom release conforme format Scene TV
- [ ] **T03.073** : Nom release contient série/émission
- [ ] **T03.074** : Nom release contient saison/episode (S01E01)
- [ ] **T03.075** : Nom release contient résolution (720p/1080p)
- [ ] **T03.076** : Nom release contient source (HDTV/WEB-DL)
- [ ] **T03.077** : Nom release contient codec (x264/x265)
- [ ] **T03.078** : Nom release contient group tag

#### 3.2.4 Structure Release TV
- [ ] **T03.079** : Dossier release créé
- [ ] **T03.080** : Vidéo copiée dans dossier release
- [ ] **T03.081** : Dossier Sample créé
- [ ] **T03.082** : Sample vidéo créé (extrait)
- [ ] **T03.083** : Sample durée < 60 secondes

#### 3.2.5 Packaging RAR TV
- [ ] **T03.084** : RAR volumes créés
- [ ] **T03.085** : RAR volumes taille conforme (rarsize MB)
- [ ] **T03.086** : RAR volumes nommés correctement
- [ ] **T03.087** : RAR méthode store (0)
- [ ] **T03.088** : RAR décompressable sans erreur

#### 3.2.6 Génération NFO TV
- [ ] **T03.089** : NFO TV généré
- [ ] **T03.090** : NFO TV contient métadonnées vidéo
- [ ] **T03.091** : NFO TV contient MediaInfo
- [ ] **T03.092** : NFO TV contient informations série (si enrichi)

#### 3.2.7 Génération SFV TV
- [ ] **T03.093** : SFV TV généré
- [ ] **T03.094** : SFV TV contient tous fichiers RAR
- [ ] **T03.095** : SFV TV CRC32 correct

#### 3.2.8 Profils TV
- [ ] **T03.096** : Profil HDTV_SD applique correctement (SD, CRF 19, 20MB)
- [ ] **T03.097** : Profil HDTV_720P applique correctement (HD, CRF 18, 50MB)
- [ ] **T03.098** : Profil HDTV_1080P applique correctement (HD, CRF 17, 50MB)
- [ ] **T03.099** : Profil WEB_SD applique correctement
- [ ] **T03.100** : Profil WEB_720P applique correctement
- [ ] **T03.101** : Profil WEB_1080P applique correctement
- [ ] **T03.102** : Profil auto-détecté depuis nom release

### 3.3 Tests Packaging DOCS

#### 3.3.1 Formats DOCS
- [ ] **T03.103** : Packaging PDF → succès
- [ ] **T03.104** : Packaging DOCX → succès
- [ ] **T03.105** : Packaging TXT → succès
- [ ] **T03.106** : Packaging DOC → succès (si supporté)
- [ ] **T03.107** : Format document non supporté → erreur

#### 3.3.2 Extraction Métadonnées DOCS
- [ ] **T03.108** : Métadonnées PDF extraites (title, author, etc.)
- [ ] **T03.109** : Métadonnées DOCX extraites
- [ ] **T03.110** : Métadonnées TXT basiques (nom fichier)

#### 3.3.3 Génération Nom Release DOCS
- [ ] **T03.111** : Nom release conforme format Scene DOCS
- [ ] **T03.112** : Nom release contient titre document
- [ ] **T03.113** : Nom release contient format (PDF/DOCX/TXT)
- [ ] **T03.114** : Nom release contient source type
- [ ] **T03.115** : Nom release contient group tag

#### 3.3.4 Structure Release DOCS
- [ ] **T03.116** : Dossier release créé
- [ ] **T03.117** : Document copié dans dossier release
- [ ] **T03.118** : Pas de Sample pour DOCS (normal)

#### 3.3.5 Packaging ZIP DOCS
- [ ] **T03.119** : ZIP DOCS créé multi-volumes
- [ ] **T03.120** : ZIP DOCS contient document
- [ ] **T03.121** : ZIP DOCS volumes conforme

#### 3.3.6 Génération NFO/DIZ/SFV DOCS
- [ ] **T03.122** : NFO DOCS généré
- [ ] **T03.123** : DIZ DOCS généré
- [ ] **T03.124** : SFV DOCS généré

### 3.4 Tests Intégration Packaging

#### 3.4.1 Workflow Complet EBOOK
- [ ] **T03.125** : Workflow complet EPUB : upload → metadata → pack → release → validation
- [ ] **T03.126** : Workflow complet MOBI : upload → metadata → pack → release → validation
- [ ] **T03.127** : Workflow complet PDF : upload → metadata → pack → release → validation

#### 3.4.2 Workflow Complet TV
- [ ] **T03.128** : Workflow complet MKV : upload → metadata → pack → release → validation

#### 3.4.3 Workflow Complet DOCS
- [ ] **T03.129** : Workflow complet PDF DOCS : upload → metadata → pack → release → validation

#### 3.4.4 Jobs et Logs
- [ ] **T03.130** : Job créé lors packaging
- [ ] **T03.131** : Job status = running pendant packaging
- [ ] **T03.132** : Job status = completed après succès
- [ ] **T03.133** : Job status = failed après erreur
- [ ] **T03.134** : Logs job contiennent étapes packaging
- [ ] **T03.135** : Logs job contiennent erreurs si échec

#### 3.4.5 Upload FTP/SFTP (si configuré)
- [ ] **T03.136** : Upload automatique FTP fonctionne
- [ ] **T03.137** : Upload automatique SFTP fonctionne
- [ ] **T03.138** : Upload retry en cas d'échec
- [ ] **T03.139** : Upload vérifie espace disque serveur
- [ ] **T03.140** : Upload logué dans job

### 3.5 Tests Performance Packaging

- [ ] **T03.141** : Packaging EPUB < 500MB → < 30 secondes
- [ ] **T03.142** : Packaging EPUB > 500MB → < 2 minutes
- [ ] **T03.143** : Packaging TV 720p → < 5 minutes
- [ ] **T03.144** : Packaging TV 1080p → < 10 minutes
- [ ] **T03.145** : Extraction métadonnées < 5 secondes
- [ ] **T03.146** : Génération ZIP multi-volumes < 1 minute/volume

### 3.6 Tests Gestion Erreurs Packaging

- [ ] **T03.147** : Fichier introuvable → erreur claire
- [ ] **T03.148** : Fichier corrompu → erreur claire
- [ ] **T03.149** : Espace disque insuffisant → erreur claire
- [ ] **T03.150** : Group invalide → erreur validation
- [ ] **T03.151** : Métadonnées manquantes → valeurs par défaut ou erreur
- [ ] **T03.152** : Échec API enrichissement → continue sans enrichissement

---

## 📋 CHECKLIST GÉNÉRALE D'EXÉCUTION

### Prérequis
- [ ] Docker et Docker Compose installés
- [ ] Fichier `.env` configuré
- [ ] Espace disque suffisant (>20GB)
- [ ] Connexion Internet (pour APIs enrichissement)
- [ ] Fichiers de test disponibles (eBooks, vidéos, docs)

### Ordre d'Exécution Recommandé

1. **Phase 1 : Tests Docker** (4-6h)
   - [ ] T01.001 à T01.091 (85 tests)
   - Documentation résultats

2. **Phase 2 : Tests Interface Web** (6-8h)
   - [ ] T02.001 à T02.183 (120 tests)
   - Documentation résultats

3. **Phase 3 : Tests Packaging** (5-7h)
   - [ ] T03.001 à T03.152 (95 tests)
   - Documentation résultats

### Documentation Résultats

Pour chaque test :
- [ ] Statut (✅ PASS / ❌ FAIL / ⚠️ SKIP)
- [ ] Temps d'exécution
- [ ] Erreurs/détails si échec
- [ ] Captures d'écran si pertinent
- [ ] Logs pertinents

---

## 🎯 CRITÈRES DE SUCCÈS

### Docker
- **Objectif** : 100% des tests T01.xxx passent
- **Critère** : Tous services démarrent, fonctionnent, persistent données

### Interface Web
- **Objectif** : 100% des tests T02.xxx passent
- **Critère** : Toutes pages accessibles, toutes fonctionnalités opérationnelles

### Packaging Release
- **Objectif** : 100% des tests T03.xxx passent
- **Critère** : Tous formats packagés correctement, releases conformes Scene Rules 2022

---

## 📊 TEMPLATE RAPPORT DE TEST

```markdown
## Test TXX.XXX : [Nom Test]

**Statut** : ✅ PASS / ❌ FAIL / ⚠️ SKIP  
**Date** : YYYY-MM-DD HH:MM:SS  
**Durée** : X.XX secondes  
**Environnement** : Docker / Local  
**Version** : vX.X.X

### Description
[Description du test]

### Prérequis
- [Liste prérequis]

### Étapes
1. [Étape 1]
2. [Étape 2]
...

### Résultat Attendu
[Résultat attendu]

### Résultat Obtenu
[Résultat obtenu]

### Erreurs/Détails
[Si échec, détails]

### Captures/Logs
[Liens captures/logs si pertinent]
```

---

## 🚀 COMMANDES UTILES POUR EXÉCUTION

### Docker
```bash
# Démarrer environnement
./start_docker.sh

# Vérifier services
docker-compose ps

# Logs
docker-compose logs -f backend

# Shell backend
docker-compose exec backend bash

# Tests manuels health
curl http://localhost:5000/health
```

### Interface Web
```bash
# Démarrer serveur local (si tests locaux)
./start_server.sh
# ou
python web/app.py

# Tests E2E
pytest tests/e2e/ -v

# Tests avec Playwright MCP
# [Utiliser outils MCP Playwright]
```

### Packaging
```bash
# Test packaging CLI
python src/packer_cli.py pack path/to/file.epub TESTGRP

# Test packaging via API
curl -X POST http://localhost:5000/api/pack \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/file.epub" \
  -F "group=TESTGRP"
```

---

**Plan créé le** : 2025-01-27  
**Statut** : ✅ **PRÊT POUR EXÉCUTION**  
**Total Tests** : **300+ tests exhaustifs**

---

## 📝 NOTES FINALES

Ce plan de tests exhaustif couvre **100% des fonctionnalités** Docker, Interface Web, et Packaging de Release. Chaque test est **indépendant, reproductible, et documenté**.

**Prochaines étapes** :
1. Exécuter Phase 1 (Docker) → Documenter résultats
2. Exécuter Phase 2 (Interface Web) → Documenter résultats
3. Exécuter Phase 3 (Packaging) → Documenter résultats
4. Analyser résultats → Créer rapport final
5. Corriger éventuels problèmes identifiés
6. Ré-exécuter tests échoués → Validation finale

**Objectif final** : **100% des tests passent** ✅

