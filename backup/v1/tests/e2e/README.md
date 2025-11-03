# Tests End-to-End (E2E)

## Vue d'ensemble

Les tests E2E valident toutes les fonctionnalités existantes de l'application via des tests automatisés utilisant `requests` et potentiellement Playwright MCP pour les interactions navigateur.

## Structure

```
tests/e2e/
├── __init__.py
├── conftest.py              # Fixtures partagées
├── test_auth_flow.py        # Tests authentification
├── test_api_endpoints.py    # Tests endpoints API
├── test_users_management.py # Tests gestion utilisateurs
├── test_configuration.py    # Tests configuration
├── fixtures/                # Fichiers de test (eBooks, vidéos)
└── README.md               # Ce fichier
```

## Prérequis

1. **Serveur Flask démarré**
   ```bash
   python web/app.py
   # ou
   ./start_server.sh
   ```

2. **Base de données MySQL initialisée**
   - Base de données `packer` créée
   - Compte admin créé (username: `admin`, password: `admin`)

3. **Dépendances installées**
   ```bash
   pip install -r requirements.txt
   pip install pytest requests
   ```

## Exécution des tests

### Tous les tests E2E
```bash
pytest tests/e2e/ -v
```

### Test spécifique
```bash
pytest tests/e2e/test_auth_flow.py -v
```

### Avec couverture
```bash
pytest tests/e2e/ --cov=web --cov-report=html
```

## Configuration

Les tests utilisent les fixtures définies dans `conftest.py` :

- `flask_server` : Vérifie que le serveur Flask est disponible sur `http://localhost:5000`
- `base_url` : URL de base du serveur
- `api_base_url` : URL de base pour les API (`/api`)
- `admin_credentials` : Credentials admin par défaut
- `auth_token` : Token JWT obtenu après login
- `auth_headers` : Headers d'authentification

## Tests disponibles

### 1. Authentification (`test_auth_flow.py`)
- ✅ Login avec credentials valides
- ✅ Login avec credentials invalides
- ✅ Récupération utilisateur courant
- ✅ Accès endpoint protégé sans authentification
- ✅ Accès endpoint protégé avec authentification

### 2. Endpoints API (`test_api_endpoints.py`)
- ✅ Jobs (liste, détails, logs, artefacts)
- ✅ Préférences (CRUD)
- ✅ Chemins (config par groupe/type)
- ✅ Destinations (CRUD FTP/SFTP)
- ✅ Utilisateurs (CRUD - admin uniquement)
- ✅ Templates (liste, détails)
- ✅ Wizard (préférences)

### 3. Gestion Utilisateurs (`test_users_management.py`)
- ✅ Liste utilisateurs
- ✅ Détails utilisateur
- ✅ Création utilisateur
- ✅ Mise à jour utilisateur
- ✅ Suppression utilisateur

### 4. Configuration (`test_configuration.py`)
- ✅ Préférences (CRUD)
- ✅ Chemins par groupe/type (CRUD)
- ✅ Destinations FTP/SFTP (CRUD)

## Notes importantes

- Les tests supposent que le serveur Flask est déjà démarré
- Les tests utilisent des credentials admin par défaut (`admin`/`admin`)
- Certains tests créent des données qui peuvent persister (nettoyage manuel si nécessaire)
- Les tests sont indépendants et peuvent être exécutés dans n'importe quel ordre

## Intégration avec Playwright MCP

Pour les tests navigateur (simulation utilisateur réel), utiliser Playwright MCP :

1. Configurer `.cursor/mcp.json` avec Playwright MCP
2. Utiliser les outils MCP pour naviguer dans l'interface web
3. Créer des tests qui simulent les interactions utilisateur

Voir `.cursor/mcp.example.json` pour la configuration.

## Résolution de problèmes

### Serveur non disponible
```bash
# Démarrer le serveur dans un terminal séparé
python web/app.py

# Ou utiliser le script
./start_server.sh
```

### Erreurs d'authentification
- Vérifier que le compte admin existe : `python web/scripts/seed_admin.py`
- Vérifier les credentials dans `conftest.py`

### Erreurs de base de données
- Vérifier que MySQL est démarré
- Vérifier la connexion : `mysql -u packer -ppacker -h localhost packer`
- Réinitialiser la base si nécessaire : `python web/scripts/init_db.py`

