# Deployment Guide

## 📋 Prérequis

- Docker et Docker Compose installés
- MySQL 8.0+ (ou via Docker)
- Variables d'environnement configurées

## 🚀 Déploiement avec Docker Compose

### 1. Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer les variables d'environnement
nano .env
```

### 2. Démarrer les services

```bash
# Construire et démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Vérifier le statut
docker-compose ps
```

### 3. Initialiser la base de données

```bash
# Exécuter les migrations
docker-compose exec backend flask db upgrade

# Optionnel : Créer un utilisateur admin
docker-compose exec backend flask create-admin
```

### 4. Accéder à l'application

- Frontend : http://localhost:8080
- Backend API : http://localhost:5000/api
- Health Check : http://localhost:8080/health

## 🛠️ Commandes Utiles

```bash
# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Reconstruire les images
docker-compose build --no-cache

# Voir les logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Redémarrer un service
docker-compose restart backend

# Exécuter une commande dans un conteneur
docker-compose exec backend flask db migrate -m "Description"
```

## 📦 Déploiement Production

### Variables d'environnement critiques

- `SECRET_KEY` : Clé secrète Flask (générer avec `secrets.token_hex(32)`)
- `JWT_SECRET_KEY` : Clé secrète JWT (générer avec `secrets.token_hex(32)`)
- `DB_PASSWORD` : Mot de passe base de données fort
- `CORS_ORIGINS` : Origines CORS autorisées (séparées par virgules)

### Sécurité

1. Ne jamais commiter `.env` dans git
2. Utiliser des secrets forts pour production
3. Activer HTTPS avec certificat SSL
4. Configurer firewall (ports 80, 443 uniquement)
5. Activer rate limiting
6. Configurer backups automatiques de la base de données

## 🔍 Monitoring

```bash
# Vérifier les health checks
docker-compose ps

# Statistiques des conteneurs
docker stats

# Logs applicatifs
docker-compose logs -f --tail=100 backend
```

## 📝 Notes

- Les migrations sont exécutées automatiquement au démarrage si configuré
- Les volumes persistent les données de la base de données
- Les logs sont stockés dans `./logs/` (monté comme volume)
