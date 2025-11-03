# 📝 Guide des Scripts Utilitaires

## Scripts Disponibles

### Scripts d'Initialisation

#### `web/scripts/init_db.py`
Initialise la base de données et exécute les migrations.

```bash
python web/scripts/init_db.py
```

#### `web/scripts/seed_admin.py`
Crée un utilisateur admin.

```bash
python web/scripts/seed_admin.py <username> <password>
```

#### `web/scripts/seed_templates.py`
Crée les templates NFO par défaut dans la base de données.

```bash
python web/scripts/seed_templates.py
```

**Templates créés :**
- `default_ebook` : Template par défaut pour releases EBOOK (marqué comme défaut)
- `default_tv` : Template pour releases TV
- `default_docs` : Template pour releases DOCS
- `minimal` : Template minimal simple

### Scripts de Configuration

#### `web/scripts/manage_apis.py`
Gère les configurations d'APIs externes.

```bash
# Lister toutes les configurations
python web/scripts/manage_apis.py list

# Ajouter une configuration API
python web/scripts/manage_apis.py add omdb YOUR_API_KEY
python web/scripts/manage_apis.py add tvdb YOUR_API_KEY --user-key YOUR_USER_KEY
python web/scripts/manage_apis.py add tmdb YOUR_API_KEY

# Tester une configuration
python web/scripts/manage_apis.py test omdb
python web/scripts/manage_apis.py test tvdb
python web/scripts/manage_apis.py test tmdb
```

### Scripts de Validation

#### `validate_project.py`
Valide que tous les fichiers essentiels sont présents.

```bash
python validate_project.py
```

**Vérifie :**
- Structure des fichiers
- Services implémentés
- Blueprints Flask
- Tests disponibles
- Documentation

#### `check_environment.py`
Vérifie que l'environnement est correctement configuré.

```bash
python check_environment.py
```

**Vérifie :**
- Version Python (3.10+)
- Dépendances installées
- Variables d'environnement
- Connexion base de données
- Utilisateur admin
- Répertoires nécessaires
- Outils externes (optionnels)

### Scripts Utilitaires

#### `scripts/generate_examples.py`
Génère des fichiers d'exemple pour configuration.

```bash
python scripts/generate_examples.py
```

**Crée :**
- `examples/batch_jobs.json` : Exemple pour batch processing
- `examples/config.json` : Exemple de configuration
- `examples/.env.example` : Exemple de variables d'environnement

### Scripts Docker

#### `start_docker.sh`
Script de démarrage complet avec Docker Compose.

```bash
./start_docker.sh
```

**Fait :**
- Vérifie Docker et Docker Compose
- Crée .env si nécessaire
- Vérifie l'environnement
- Démarre les services
- Initialise la base de données
- Crée utilisateur admin
- Crée templates par défaut
- Vérifie health check

## Utilisation dans Docker

Tous les scripts peuvent être exécutés dans le container Docker :

```bash
# Initialiser DB
docker-compose exec backend python web/scripts/init_db.py

# Créer admin
docker-compose exec backend python web/scripts/seed_admin.py admin password123

# Créer templates
docker-compose exec backend python web/scripts/seed_templates.py

# Gérer APIs
docker-compose exec backend python web/scripts/manage_apis.py list
docker-compose exec backend python web/scripts/manage_apis.py add omdb YOUR_KEY

# Vérifier environnement
docker-compose exec backend python check_environment.py
```

## Exemples d'Utilisation

### Setup Complet

```bash
# 1. Démarrer Docker
./start_docker.sh

# 2. Configurer APIs (optionnel)
docker-compose exec backend python web/scripts/manage_apis.py add omdb YOUR_KEY
docker-compose exec backend python web/scripts/manage_apis.py test omdb

# 3. Vérifier que tout fonctionne
docker-compose exec backend python check_environment.py
```

### Maintenance

```bash
# Créer nouveau template
docker-compose exec backend python web/scripts/seed_templates.py

# Ajouter nouvelle API
docker-compose exec backend python web/scripts/manage_apis.py add tmdb YOUR_KEY

# Vérifier santé système
curl http://localhost:5000/health
```

## Notes

- Tous les scripts nécessitent un contexte Flask valide
- Les scripts DB nécessitent une connexion MySQL active
- Les scripts API nécessitent un utilisateur admin existant
- Les scripts Docker utilisent le container `backend`
