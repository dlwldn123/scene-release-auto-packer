# 🎯 Checklist de Déploiement Production

## Pré-Déploiement

### ✅ Sécurité

- [ ] Générer clés sécurisées (JWT_SECRET_KEY, API_KEYS_ENCRYPTION_KEY)
  ```bash
  openssl rand -hex 32
  ```
- [ ] Modifier mots de passe par défaut (MySQL, admin)
- [ ] Configurer firewall (ports 3306, 5000)
- [ ] Configurer SSL/TLS (reverse proxy)
- [ ] Vérifier permissions fichiers sensibles

### ✅ Base de Données

- [ ] Créer base de données MySQL
- [ ] Configurer utilisateur MySQL avec permissions minimales
- [ ] Exécuter migrations : `python web/scripts/init_db.py`
- [ ] Créer utilisateur admin : `python web/scripts/seed_admin.py admin <secure_password>`
- [ ] Configurer backup automatique MySQL

### ✅ Configuration

- [ ] Configurer `.env` avec valeurs production
- [ ] Configurer APIs externes (optionnel)
  ```bash
  python web/scripts/manage_apis.py add omdb YOUR_KEY
  ```
- [ ] Créer templates NFO par défaut : `python web/scripts/seed_templates.py`
- [ ] Configurer destinations FTP/SFTP si nécessaire

### ✅ Docker

- [ ] Vérifier Docker et Docker Compose installés
- [ ] Tester build : `docker-compose build`
- [ ] Tester démarrage : `./start_docker.sh`
- [ ] Vérifier health checks : `curl http://localhost:5000/health`
- [ ] Configurer volumes persistants

### ✅ Tests

- [ ] Exécuter validation : `python validate_project.py`
- [ ] Vérifier environnement : `python check_environment.py`
- [ ] Exécuter tests unitaires : `pytest tests/`
- [ ] Tester packaging manuel (EBOOK, TV, DOCS)

## Déploiement

### ✅ Services

- [ ] Démarrer services : `docker-compose up -d`
- [ ] Vérifier logs : `docker-compose logs -f backend`
- [ ] Vérifier santé : `curl http://localhost:5000/health`
- [ ] Tester authentification : Login via interface web
- [ ] Tester packaging : Créer une release test

### ✅ Reverse Proxy (Recommandé)

- [ ] Configurer Nginx ou Traefik
- [ ] Configurer SSL/TLS (Let's Encrypt)
- [ ] Configurer domain name
- [ ] Tester accès via domain

### ✅ Monitoring

- [ ] Configurer monitoring (Prometheus, Grafana, etc.)
- [ ] Configurer alertes (logs erreurs, downtime)
- [ ] Configurer rotation logs
- [ ] Configurer monitoring disque (volumes)

## Post-Déploiement

### ✅ Vérifications

- [ ] Vérifier tous les endpoints API
- [ ] Tester packaging complet (EBOOK, TV, DOCS)
- [ ] Vérifier upload FTP/SFTP
- [ ] Vérifier génération NFO/DIZ/SFV
- [ ] Vérifier jobs et logs

### ✅ Documentation

- [ ] Documenter configuration spécifique
- [ ] Documenter accès et credentials
- [ ] Documenter procédures de backup
- [ ] Documenter procédures de restauration

### ✅ Maintenance

- [ ] Planifier backups réguliers
- [ ] Planifier mise à jour dépendances
- [ ] Planifier rotation logs
- [ ] Configurer monitoring disque

## Configuration Recommandée Production

### Variables d'Environnement

```bash
# Sécurité
JWT_SECRET_KEY=<généré avec openssl rand -hex 32>
API_KEYS_ENCRYPTION_KEY=<généré avec openssl rand -hex 32>

# Base de données
DATABASE_URL=mysql+pymysql://packer_user:secure_password@db_host:3306/packer_db

# Environnement
FLASK_ENV=production

# Logs
LOG_LEVEL=INFO
```

### Docker Compose Production

Modifications recommandées :
- Augmenter workers Gunicorn (selon CPU)
- Configurer limits ressources
- Configurer restart policy
- Configurer réseau isolé
- Configurer volumes nommés pour backups

### Sécurité Supplémentaire

- [ ] Utiliser secrets Docker pour credentials
- [ ] Configurer réseau Docker isolé
- [ ] Désactiver ports MySQL exposés (si possible)
- [ ] Configurer rate limiting sur reverse proxy
- [ ] Configurer CORS restrictif
- [ ] Activer logging audit

## Support et Maintenance

### Commandes Utiles

```bash
# Voir logs
docker-compose logs -f backend

# Redémarrer service
docker-compose restart backend

# Backup base de données
docker-compose exec mysql mysqldump -u packer -ppacker packer > backup.sql

# Restaurer base de données
docker-compose exec -T mysql mysql -u packer -ppacker packer < backup.sql

# Vérifier santé
curl http://localhost:5000/health

# Accéder au shell
docker-compose exec backend bash
```

### Troubleshooting

**Problème : Service ne démarre pas**
```bash
docker-compose logs backend
docker-compose ps
```

**Problème : Base de données inaccessible**
```bash
docker-compose exec mysql mysqladmin ping -h localhost -u root -p
```

**Problème : Permissions fichiers**
```bash
docker-compose exec backend chown -R appuser:appuser /app/releases
```

## Notes

- Toutes les commandes doivent être adaptées selon votre environnement
- Vérifier régulièrement les mises à jour de sécurité
- Maintenir backups réguliers
- Monitorer l'utilisation des ressources
