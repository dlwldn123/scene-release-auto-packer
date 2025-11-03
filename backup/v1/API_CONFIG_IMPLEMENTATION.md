# Implémentation Blueprint API Config

## Statut : ✅ TERMINÉ

## Date : 2025-01-27

## Résumé

L'implémentation complète du Blueprint API Config est **terminée**. Tous les endpoints nécessaires pour la configuration des APIs externes ont été créés avec validation et tests.

## ✅ Composants Implémentés

### 1. Blueprint API Config (`web/blueprints/api_config.py`)

**Endpoints créés :**

- `GET /api/config/apis` - Liste configs APIs (admin voit toutes, user voit les siennes)
- `POST /api/config/apis` - Créer/mettre à jour config API
- `GET /api/config/apis/<api_name>` - Récupérer config API spécifique
- `PUT /api/config/apis/<api_name>` - Mettre à jour config API
- `DELETE /api/config/apis/<api_name>` - Supprimer config API (admin uniquement)
- `POST /api/config/apis/<api_name>/test` - Tester connexion API

**Fonctionnalités :**
- ✅ Protection admin/user (admin voit toutes, user voit les siennes)
- ✅ Validation schémas Marshmallow
- ✅ Masquage clés API (jamais exposées en clair)
- ✅ Test connexion pour OMDb, TVDB, TMDb, OpenLibrary
- ✅ Support création/mise à jour en un seul endpoint (POST)

### 2. Schémas Marshmallow (`web/schemas/api_config.py`)

**Schémas créés :**
- `ApiConfigSchema` - Sérialisation (masque clé API)
- `ApiConfigCreateSchema` - Validation création (api_name + api_data)
- `ApiConfigUpdateSchema` - Validation mise à jour (api_data)
- `ApiConfigTestSchema` - Résultat test connexion

**Validations :**
- ✅ api_name doit être dans ['omdb', 'tvdb', 'tmdb', 'openlibrary']
- ✅ api_data doit contenir au moins une clé
- ✅ TVDB nécessite api_key et user_key
- ✅ Clés API toujours masquées dans les réponses

### 3. Fonction Test Connexion (`_test_api_connection()`)

**APIs supportées :**
- ✅ **OMDb** : Test avec recherche simple (apikey + titre)
- ✅ **TVDB** : Test authentification JWT (apikey + userkey)
- ✅ **TMDb** : Test avec endpoint configuration
- ✅ **OpenLibrary** : Test avec recherche (pas de clé requise)

**Gestion erreurs :**
- ✅ Timeout (10s)
- ✅ Erreurs réseau
- ✅ Erreurs API (messages clairs)

### 4. Enregistrement dans app.py

- ✅ Blueprint importé et enregistré avec `url_prefix='/api/config'`
- ✅ Routes finales : `/api/config/apis`, `/api/config/apis/<api_name>`, etc.

### 5. Tests Unitaires (`tests/test_api_config.py`)

**9 tests créés :**
- ✅ `test_list_api_configs` - Liste configs
- ✅ `test_create_api_config` - Création config
- ✅ `test_get_api_config` - Récupération config (clé masquée)
- ✅ `test_update_api_config` - Mise à jour config
- ✅ `test_delete_api_config` - Suppression config
- ✅ `test_test_api_connection` - Test connexion API
- ✅ `test_api_config_requires_auth` - Protection authentification
- ✅ `test_delete_requires_admin` - Protection admin pour suppression

## 📋 Utilisation

### Créer/Mettre à jour Config API

```bash
curl -X POST http://localhost:5000/api/config/apis \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "api_name": "omdb",
    "api_data": {"api_key": "your_api_key"}
  }'
```

### Récupérer Config API

```bash
curl -X GET http://localhost:5000/api/config/apis/omdb \
  -H "Authorization: Bearer <token>"
```

### Tester Connexion API

```bash
curl -X POST http://localhost:5000/api/config/apis/omdb/test \
  -H "Authorization: Bearer <token>"
```

### Supprimer Config API (admin uniquement)

```bash
curl -X DELETE http://localhost:5000/api/config/apis/omdb \
  -H "Authorization: Bearer <token>"
```

## 🔧 Configuration APIs

### OMDb
```json
{
  "api_name": "omdb",
  "api_data": {
    "api_key": "your_omdb_api_key"
  }
}
```

### TVDB
```json
{
  "api_name": "tvdb",
  "api_data": {
    "api_key": "your_tvdb_api_key",
    "user_key": "your_tvdb_user_key",
    "username": "your_username"  // Optionnel
  }
}
```

### TMDb
```json
{
  "api_name": "tmdb",
  "api_data": {
    "api_key": "your_tmdb_api_key"
  }
}
```

### OpenLibrary
```json
{
  "api_name": "openlibrary",
  "api_data": {}  // Pas de clé API requise
}
```

## 🔐 Sécurité

- ✅ Clés API chiffrées au repos (Fernet)
- ✅ Clés API jamais exposées en clair dans les réponses
- ✅ Masquage automatique (`***`)
- ✅ Protection admin/user
- ✅ Validation stricte des données

## ✅ Checklist Implémentation

- [x] Blueprint `api_config` créé
- [x] Endpoints CRUD complets
- [x] Endpoint test connexion
- [x] Schémas Marshmallow
- [x] Validation spécifique TVDB
- [x] Masquage clés API
- [x] Protection admin/user
- [x] Tests unitaires
- [x] Enregistrement dans app.py
- [x] Documentation

## 🚀 Prochaines Étapes

1. Intégrer dans `MetadataEnricher` pour utiliser les clés depuis `ApiConfig`
2. Intégrer dans wizard pour permettre configuration APIs depuis l'interface
3. Créer interface frontend pour configuration APIs
4. Tests E2E pour configuration APIs

