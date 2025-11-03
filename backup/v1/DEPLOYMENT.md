# DEPLOYMENT.md

## Déploiement avec Docker Compose

### Prérequis

- Docker >= 20.10
- Docker Compose >= 2.0
- Git

### Installation

1. **Cloner le dépôt**
```bash
git clone <repository-url>
cd ebook.scene.packer
```

2. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

**Important** : Générer des clés sécurisées :
```bash
# Générer JWT_SECRET_KEY
openssl rand -hex 32

# Générer API_KEYS_ENCRYPTION_KEY
openssl rand -hex 32
```

3. **Construire et démarrer les services**
```bash
docker-compose up -d --build
```

### Initialisation de la base de données

Une fois les services démarrés :

```bash
# Initialiser la base de données
docker-compose exec backend python web/scripts/init_db.py

# Créer un utilisateur admin
docker-compose exec backend python web/scripts/seed_admin.py admin password123
```

### Accès à l'application

- **Interface Web** : http://localhost:5000
- **API** : http://localhost:5000/api
- **Health Check** : http://localhost:5000/health

### Gestion des services

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f backend

# Redémarrer un service
docker-compose restart backend

# Accéder au shell du container backend
docker-compose exec backend bash
```

### Volumes persistants

Les données sont stockées dans des volumes Docker :
- `mysql_data` : Base de données MySQL
- `releases_data` : Releases générées
- `uploads_data` : Fichiers uploadés
- `logs_data` : Logs application

Pour sauvegarder :
```bash
docker-compose exec mysql mysqldump -u packer -ppacker packer > backup.sql
```

### Configuration Production

Pour la production, recommandations :

1. **Utiliser un reverse proxy** (Nginx, Traefik) devant le backend
2. **Configurer SSL/TLS** avec Let's Encrypt
3. **Modifier les secrets** dans `.env`
4. **Configurer les backups** automatiques MySQL
5. **Monitorer les logs** avec un système de logging centralisé

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `MYSQL_ROOT_PASSWORD` | Mot de passe root MySQL | `rootpassword` |
| `MYSQL_DATABASE` | Nom de la base de données | `packer` |
| `MYSQL_USER` | Utilisateur MySQL | `packer` |
| `MYSQL_PASSWORD` | Mot de passe MySQL | `packer` |
| `JWT_SECRET_KEY` | Clé secrète JWT | (générer) |
| `API_KEYS_ENCRYPTION_KEY` | Clé chiffrement API keys | (générer) |
| `FLASK_ENV` | Environnement Flask | `production` |
| `BACKEND_PORT` | Port backend | `5000` |

### Dépannage

**Le backend ne démarre pas :**
```bash
docker-compose logs backend
# Vérifier les erreurs de connexion MySQL
```

**Erreur de connexion MySQL :**
- Vérifier que le service MySQL est démarré : `docker-compose ps`
- Vérifier les variables d'environnement dans `.env`
- Attendre que MySQL soit complètement démarré (healthcheck)

**Erreur de permissions :**
```bash
docker-compose exec backend chown -R appuser:appuser /app/releases
```

### Migration depuis installation locale

1. Exporter les données MySQL locales
2. Importer dans le container MySQL
3. Copier les releases dans le volume `releases_data`
4. Redémarrer les services
