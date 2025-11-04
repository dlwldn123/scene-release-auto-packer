# 🚀 Guide de Déploiement Rapide - eBook Scene Packer v2

**Date** : 2025-11-03  
**Version** : 2.0.0  
**Statut** : ✅ Production-Ready

---

## 📋 Vue d'Ensemble

Ce document fournit un guide rapide pour déployer l'application eBook Scene Packer v2 en production.

**Pour un guide détaillé** : Voir `docs/DEPLOYMENT_PLAN.md`

---

## 🐳 Déploiement avec Docker Compose

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disque minimum

### Configuration

**1. Variables d'environnement** (`.env`)

```bash
# Database
DB_ROOT_PASSWORD=changeme_secure_password
DB_NAME=ebook_scene_packer
DB_USER=appuser
DB_PASSWORD=changeme_secure_password
DB_PORT=3306

# Backend
FLASK_ENV=production
JWT_SECRET_KEY=changeme_very_secure_secret_key_min_32_chars
JWT_ACCESS_TOKEN_EXPIRES=3600
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=INFO

# Ports
BACKEND_PORT=5000
FRONTEND_PORT=80
NGINX_PORT=8080
```

**2. Démarrage**

```bash
# Build et démarrage
docker-compose up -d --build

# Vérifier logs
docker-compose logs -f

# Vérifier statut
docker-compose ps
```

**3. Initialisation Base de Données**

```bash
# Migrations
docker-compose exec backend flask db upgrade

# Créer utilisateur admin (si script existe)
docker-compose exec backend flask create-admin
```

---

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

---

## 🔒 Sécurité Production

### Variables d'environnement critiques

- `SECRET_KEY` : Clé secrète Flask (générer avec `secrets.token_hex(32)`)
- `JWT_SECRET_KEY` : Clé secrète JWT (générer avec `secrets.token_hex(32)`)
- `DB_PASSWORD` : Mot de passe base de données fort
- `CORS_ORIGINS` : Origines CORS autorisées (séparées par virgules)

### Bonnes Pratiques

1. Ne jamais commiter `.env` dans git
2. Utiliser des secrets forts pour production
3. Activer HTTPS avec certificat SSL
4. Configurer firewall (ports 80, 443 uniquement)
5. Activer rate limiting
6. Configurer backups automatiques de la base de données

---

## 🔍 Monitoring

```bash
# Vérifier les health checks
docker-compose ps

# Statistiques des conteneurs
docker stats

# Logs applicatifs
docker-compose logs -f backend
```

---

## 📚 Documentation Complète

Pour un guide déploiement complet incluant :
- Architecture de déploiement
- Déploiement Kubernetes
- SSL/TLS Configuration
- Monitoring Production
- Mises à jour et Rollback

---

**Dernière mise à jour** : 2025-11-03
```

## 📝 Notes

- Les migrations sont exécutées automatiquement au démarrage si configuré
- Les volumes persistent les données de la base de données
- Les logs sont stockés dans `./logs/` (monté comme volume)
