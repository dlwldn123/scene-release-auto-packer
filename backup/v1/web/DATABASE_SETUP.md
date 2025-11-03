# Setup Guide - Base de données et authentification

## Prérequis

1. MySQL installé et démarré
2. Python 3.10+ avec virtualenv activé
3. Dépendances installées : `pip install -r requirements.txt`

## Configuration Base de Données

### 1. Créer la base de données MySQL

```bash
mysql -u root -p
CREATE DATABASE packer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'packer'@'localhost' IDENTIFIED BY 'packer';
GRANT ALL PRIVILEGES ON packer.* TO 'packer'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2. Configurer la connexion

Définir la variable d'environnement `DATABASE_URL` :

```bash
export DATABASE_URL="mysql+pymysql://packer:packer@localhost:3306/packer"
```

Ou modifier `web/config.py` pour ajuster la valeur par défaut.

### 3. Initialiser la base de données

```bash
# Créer les tables
python web/scripts/init_db.py

# Ou utiliser Flask-Migrate (recommandé pour production)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Créer le compte admin

```bash
# Compte admin par défaut (username: admin, password: admin)
python web/scripts/seed_admin.py

# Ou personnaliser
python web/scripts/seed_admin.py --username admin --password changeme --email admin@example.com
```

## Configuration JWT

Définir la variable d'environnement `JWT_SECRET_KEY` :

```bash
export JWT_SECRET_KEY="your-secret-key-here-change-in-production"
```

## Configuration Chiffrement API Keys

Pour chiffrer les clés API stockées en base, générer une clé Fernet :

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Puis définir la variable d'environnement :

```bash
export API_KEYS_ENCRYPTION_KEY="votre-clé-générée"
```

## Démarrage

```bash
# Démarrer le serveur Flask
python web/app.py

# Ou utiliser le script
./web/start.sh
```

## Test Authentification

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Récupérer token depuis réponse, puis:
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

## Migrations Flask-Migrate

Pour créer de nouvelles migrations :

```bash
# Initialiser (première fois)
flask db init

# Créer migration
flask db migrate -m "Description des changements"

# Appliquer migration
flask db upgrade

# Rollback (si nécessaire)
flask db downgrade
```
