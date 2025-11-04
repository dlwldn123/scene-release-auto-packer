# Security - eBook Scene Packer v2

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 🔒 Vue d'Ensemble Sécurité

Ce document décrit les mesures de sécurité implémentées dans le projet eBook Scene Packer v2.

---

## ✅ Mesures de Sécurité Implémentées

### 1. Authentification JWT

**État** : ✅ Implémenté

**Fonctionnalités** :
- Authentification basée sur JWT (JSON Web Tokens)
- Tokens avec expiration (15 minutes access, 7 jours refresh)
- Refresh token automatique
- Validation tokens côté serveur

**Code** :
```python
# web/blueprints/auth.py
@auth_bp.route('/login', methods=['POST'])
def login():
    # Validation credentials
    # Génération tokens JWT
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })
```

**Sécurité** :
- ✅ Tokens signés avec secret key
- ✅ Expiration configurée
- ✅ Validation côté serveur

---

### 2. Rate Limiting

**État** : ✅ Implémenté

**Configuration** :
- `/api/auth/login` : **5 tentatives / 15 min**
- `/api/auth/refresh` : **10 requêtes / min**
- `/api/wizard/*` : **20 requêtes / min**
- `/api/*` : **100 requêtes / min** (global)

**Code** :
```python
# web/app.py
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# web/blueprints/auth.py
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def login():
    # ...
```

**Avantages** :
- ✅ Protection contre brute force attacks
- ✅ Protection contre DoS
- ✅ Limitation charge serveur

---

### 3. CORS (Cross-Origin Resource Sharing)

**État** : ✅ Implémenté

**Configuration** :
- Whitelist origines autorisées (configurable via env)
- Headers autorisés : `Content-Type`, `Authorization`
- Méthodes autorisées : `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`

**Code** :
```python
# web/app.py
CORS(app, resources={
    r"/api/*": {
        "origins": app.config.get("CORS_ORIGINS", ["http://localhost:8080"]),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

**Avantages** :
- ✅ Contrôle strict des origines autorisées
- ✅ Protection contre CSRF
- ✅ Headers limités

---

### 4. Security Headers

**État** : ✅ Implémenté

**Headers ajoutés** :
- `X-Content-Type-Options: nosniff` : Empêche MIME type sniffing
- `X-Frame-Options: DENY` : Empêche clickjacking
- `X-XSS-Protection: 1; mode=block` : Protection XSS
- `Strict-Transport-Security` : HSTS (production uniquement)

**Code** :
```python
# web/app.py
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if app.config.get('ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

**Avantages** :
- ✅ Protection contre MIME type sniffing
- ✅ Protection contre clickjacking
- ✅ Protection XSS
- ✅ HSTS en production

---

### 5. Validation Input

**État** : ✅ Implémenté

**Fonctionnalités** :
- Validation avec Marshmallow schemas
- Validation côté serveur (jamais côté client uniquement)
- Sanitization inputs

**Code** :
```python
# web/blueprints/auth.py
from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=8))

@auth_bp.route('/login', methods=['POST'])
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
```

**Avantages** :
- ✅ Protection contre injection SQL
- ✅ Protection contre XSS
- ✅ Validation stricte

---

### 6. Password Hashing

**État** : ✅ Implémenté

**Fonctionnalités** :
- Hashage mots de passe avec bcrypt
- Salt automatique
- Ne jamais stocker mots de passe en clair

**Code** :
```python
# web/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
```

**Avantages** :
- ✅ Mots de passe jamais en clair
- ✅ Protection contre rainbow tables
- ✅ Hashage sécurisé (bcrypt)

---

## 🚫 Vulnérabilités Identifiées et Résolues

### 1. Rate Limiting Manquant ✅ RÉSOLU

**Problème** : Pas de rate limiting sur endpoints critiques  
**Risque** : Brute force attacks, DoS  
**Solution** : Flask-Limiter implémenté

### 2. CORS Non Configuré ✅ RÉSOLU

**Problème** : CORS non configuré  
**Risque** : CSRF attacks  
**Solution** : Flask-CORS configuré avec whitelist

### 3. Security Headers Manquants ✅ RÉSOLU

**Problème** : Security headers manquants  
**Risque** : Clickjacking, XSS, MIME type sniffing  
**Solution** : Security headers middleware ajouté

---

## 📋 Checklist Sécurité

### Authentification
- [x] JWT tokens implémentés
- [x] Expiration tokens configurée
- [x] Refresh token automatique
- [x] Password hashing (bcrypt)

### Protection
- [x] Rate limiting (Flask-Limiter)
- [x] CORS configuré
- [x] Security headers
- [x] Input validation (Marshmallow)

### À Implémenter (Futur)
- [ ] Audit logging (actions critiques)
- [ ] 2FA (Two-Factor Authentication)
- [ ] Session management amélioré
- [ ] Content Security Policy (CSP)

---

## 🔗 Références

- Flask-JWT-Extended : https://flask-jwt-extended.readthedocs.io/
- Flask-Limiter : https://flask-limiter.readthedocs.io/
- Flask-CORS : https://flask-cors.readthedocs.io/
- OWASP Top 10 : https://owasp.org/www-project-top-ten/

---

**Dernière mise à jour** : 2025-11-03
