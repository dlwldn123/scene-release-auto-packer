# 🚀 Guide de Démarrage Rapide

## Installation Rapide

### Option 1 : Docker (Recommandé)

```bash
# 1. Cloner le projet
git clone <repository-url>
cd ebook.scene.packer

# 2. Copier et configurer variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 3. Générer clés sécurisées
openssl rand -hex 32 > .env.jwt_secret
openssl rand -hex 32 > .env.api_key_encryption

# Ajouter dans .env :
# JWT_SECRET_KEY=$(cat .env.jwt_secret)
# API_KEYS_ENCRYPTION_KEY=$(cat .env.api_key_encryption)

# 4. Démarrer avec Docker
./start_docker.sh

# 5. Accéder à l'application
# Interface Web: http://localhost:5000
# Health Check: http://localhost:5000/health
```

### Option 2 : Installation Locale

```bash
# 1. Créer virtualenv
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Configurer MySQL
# Créer base de données 'packer'
mysql -u root -p
CREATE DATABASE packer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'packer'@'localhost' IDENTIFIED BY 'packer';
GRANT ALL PRIVILEGES ON packer.* TO 'packer'@'localhost';
FLUSH PRIVILEGES;

# 4. Configurer variables d'environnement
export DATABASE_URL="mysql+pymysql://packer:packer@localhost:3306/packer"
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export API_KEYS_ENCRYPTION_KEY="$(openssl rand -hex 32)"

# 5. Initialiser base de données
python web/scripts/init_db.py

# 6. Créer utilisateur admin
python web/scripts/seed_admin.py admin password123

# 7. Démarrer serveur
python web/app.py
```

## Première Utilisation

### 1. Se connecter

- URL : http://localhost:5000
- Identifiants par défaut :
  - Username : `admin`
  - Password : `admin` (ou celui défini dans seed)

### 2. Créer une release EBOOK

```bash
# Via CLI
python src/packer_cli.py pack \
  --type EBOOK \
  --file book.epub \
  --group MYGRP \
  --output-dir releases

# Via API
curl -X POST http://localhost:5000/api/wizard/pack \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "EBOOK",
    "file_path": "/path/to/book.epub",
    "group": "MYGRP"
  }'
```

### 3. Vérifier les jobs

```bash
# Via CLI
python src/packer_cli.py list-jobs

# Via API
curl http://localhost:5000/api/jobs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Configuration Initiale

### 1. Configurer destinations FTP/SFTP

```bash
curl -X POST http://localhost:5000/api/destinations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My FTP Server",
    "type": "ftp",
    "host": "ftp.example.com",
    "port": 21,
    "username": "user",
    "password": "pass",
    "path": "/uploads"
  }'
```

### 2. Configurer APIs externes

```bash
curl -X POST http://localhost:5000/api/config/apis \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "api_name": "omdb",
    "api_key": "your_api_key",
    "enabled": true
  }'
```

### 3. Créer template NFO personnalisé

```bash
curl -X POST http://localhost:5000/api/templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Template",
    "content": "Title: {{title}}\nAuthor: {{author}}",
    "is_default": false
  }'
```

## Tests

### Exécuter tous les tests

```bash
# Tests unitaires et intégration
python tests/run_all_tests.py

# Tests E2E (nécessite serveur Flask démarré)
pytest tests/e2e/ -v
```

### Validation projet

```bash
python validate_project.py
```

## Structure du Projet

```
ebook.scene.packer/
├── src/                    # Code source principal
│   ├── packer.py          # Packaging EBOOK
│   ├── packaging/         # Modules packaging
│   ├── metadata/          # Métadonnées
│   └── video/             # Packaging TV
├── web/                    # Interface web Flask
│   ├── app.py             # Application principale
│   ├── blueprints/        # Routes API
│   ├── models/            # Modèles SQLAlchemy
│   ├── services/          # Services métier
│   └── schemas/           # Schémas Marshmallow
├── tests/                  # Tests
│   ├── e2e/              # Tests end-to-end
│   └── test_*.py         # Tests unitaires/intégration
├── Dockerfile             # Image Docker
├── docker-compose.yml     # Configuration Docker
└── requirements.txt       # Dépendances Python
```

## Commandes Utiles

### Docker

```bash
# Voir logs
docker-compose logs -f backend

# Redémarrer service
docker-compose restart backend

# Accéder au shell
docker-compose exec backend bash

# Arrêter services
docker-compose down
```

### CLI

```bash
# Packager un fichier
python src/packer_cli.py pack --type EBOOK --file book.epub --group MYGRP

# Batch processing
python src/packer_cli.py batch --file jobs.json

# Lister jobs
python src/packer_cli.py list-jobs

# Voir logs d'un job
python src/packer_cli.py logs <job_id>

# Gérer préférences
python src/packer_cli.py prefs get
python src/packer_cli.py prefs set key value
```

## Dépannage

### Problème : Base de données non accessible

```bash
# Vérifier connexion MySQL
mysql -u packer -p packer

# Vérifier variables d'environnement
echo $DATABASE_URL

# Recréer base de données
python web/scripts/init_db.py
```

### Problème : Token JWT invalide

```bash
# Vérifier JWT_SECRET_KEY
echo $JWT_SECRET_KEY

# Recréer utilisateur admin
python web/scripts/seed_admin.py admin newpassword
```

### Problème : Templates NFO non trouvés

```bash
# Vérifier templates dans DB
python -c "from web.app import create_app; from web.database import db; from web.models.template import NfoTemplate; app = create_app(); app.app_context().push(); print(NfoTemplate.query.all())"
```

## Documentation Complète

- **[DEPLOYMENT.md](DEPLOYMENT.md)** : Guide déploiement détaillé
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** : Vue d'ensemble complète
- **[ITERATION_LOG.md](ITERATION_LOG.md)** : Journal de progression
- **[RMD.md](RMD.md)** : Release Management Document
- **[tests/e2e/README.md](tests/e2e/README.md)** : Documentation tests E2E

## Scripts Utilitaires

Voir **[SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md)** pour guide complet des scripts.

### Scripts Principaux

```bash
# Vérifier environnement
python check_environment.py

# Valider structure projet
python validate_project.py

# Gérer APIs externes
python web/scripts/manage_apis.py list
python web/scripts/manage_apis.py add omdb YOUR_KEY

# Créer templates par défaut
python web/scripts/seed_templates.py
```

## Support

Pour toute question :
1. Consulter **[SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md)** pour scripts utilitaires
2. Consulter **[DEPLOYMENT.md](DEPLOYMENT.md)** pour déploiement
3. Consulter **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** pour checklist production
4. Vérifier les logs : `docker-compose logs -f backend`
5. Vérifier health check : `curl http://localhost:5000/health`
4. Valider structure : `python validate_project.py`