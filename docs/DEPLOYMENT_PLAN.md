# 🚀 Plan de Déploiement - eBook Scene Packer v2

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 📋 Vue d'Ensemble

Ce document décrit le plan de déploiement complet pour l'application eBook Scene Packer v2 en production.

---

## 🎯 Architecture de Déploiement

### Architecture Recommandée

```
Internet
  ↓
Nginx (Reverse Proxy + Load Balancer)
  ↓
┌─────────────┬─────────────┬─────────────┐
│ Flask App 1 │ Flask App 2 │ Flask App 3 │ (Gunicorn workers)
└─────────────┴─────────────┴─────────────┘
  ↓
MySQL (Primary + Replica)
Redis (Cache + Sessions)
```

### Composants

- **Frontend** : React 19 (build statique) → Nginx
- **Backend** : Flask 3.1.2 → Gunicorn (4 workers) → Nginx
- **Database** : MySQL 8.0 (Primary + Replica pour scaling)
- **Cache** : Redis (pour Flask-Caching)
- **Reverse Proxy** : Nginx (load balancing, SSL termination)

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

# Redis (si utilisé)
REDIS_URL=redis://redis:6379/0
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

## 🚀 Déploiement Production

### Option 1 : Docker Compose (Simple)

**Avantages** :
- Simple à mettre en place
- Bon pour petites/moyennes installations
- Tous services dans un seul fichier

**Limitations** :
- Pas de scaling automatique
- Pas de haute disponibilité native

**Configuration** :

```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2 : Kubernetes (Avancé)

**Avantages** :
- Scaling automatique
- Haute disponibilité
- Rolling updates

**Configuration** :

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/yourorg/ebook-scene-packer:latest-backend
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

---

## 🔒 Sécurité Production

### SSL/TLS

**Configuration Nginx SSL** :

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # ... reste de la config
}
```

**Let's Encrypt (Recommandé)** :

```bash
# Installer certbot
apt-get install certbot python3-certbot-nginx

# Obtenir certificat
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Renouvellement automatique
certbot renew --dry-run
```

### Secrets Management

**Jamais stocker secrets en clair** :

- ✅ Utiliser variables d'environnement
- ✅ Utiliser secrets managers (AWS Secrets Manager, HashiCorp Vault)
- ✅ Utiliser Kubernetes secrets
- ❌ JAMAIS commits secrets dans git

---

## 📊 Monitoring Production

### Health Checks

**Endpoint `/api/health`** :

```bash
# Vérifier santé application
curl http://localhost:8080/api/health

# Réponse attendue
{
  "status": "healthy",
  "timestamp": "2025-11-03T12:00:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "disk": {"free_percent": 85.2, "status": "healthy"},
    "memory": {"percent_used": 45.3, "status": "healthy"}
  }
}
```

### Métriques Prometheus

**Endpoint `/metrics`** :

```bash
# Exporter métriques
curl http://localhost:5000/metrics
```

**Grafana Dashboard** :

- Configurer datasource Prometheus
- Importer dashboard depuis `docs/MONITORING.md`
- Configurer alertes

---

## 🔄 Mises à Jour

### Processus de Déploiement

**1. Préparation** :

```bash
# Pull dernières modifications
git pull origin main

# Vérifier tests passent
pytest tests/ -v

# Build nouvelles images
docker-compose build
```

**2. Déploiement** :

```bash
# Déploiement sans downtime (rolling update)
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend

# Vérifier santé
curl http://localhost:8080/api/health
```

**3. Rollback** :

```bash
# Si problème, rollback
docker-compose pull previous-version
docker-compose up -d --no-deps backend frontend
```

---

## 📋 Checklist Déploiement

### Avant Déploiement

- [ ] Variables d'environnement configurées
- [ ] Secrets sécurisés (pas en clair)
- [ ] Base de données backup effectué
- [ ] Tests passent (100%)
- [ ] Coverage ≥90%
- [ ] Documentation à jour

### Pendant Déploiement

- [ ] Build images Docker réussis
- [ ] Containers démarrent correctement
- [ ] Migrations DB exécutées
- [ ] Health checks passent
- [ ] Monitoring configuré

### Après Déploiement

- [ ] Application accessible
- [ ] Tests smoke passent
- [ ] Monitoring actif
- [ ] Logs vérifiés
- [ ] Performance acceptable

---

## 🔗 Références

- Docker Compose : `docker-compose.yml`
- Dockerfiles : `Dockerfile`, `frontend/Dockerfile`
- Nginx Config : `nginx/nginx.conf`
- Monitoring : `docs/MONITORING.md`
- Security : `docs/SECURITY.md`

---

**Dernière mise à jour** : 2025-11-03
