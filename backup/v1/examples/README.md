# 📦 Exemples de Configuration

Ce dossier contient des exemples de fichiers de configuration pour vous aider à démarrer rapidement.

## Fichiers Disponibles

### `batch_jobs.json`
Exemple de fichier JSON pour batch processing avec le CLI.

**Utilisation :**
```bash
python src/packer_cli.py batch --file examples/batch_jobs.json
```

**Structure :**
```json
{
  "jobs": [
    {
      "type": "EBOOK",
      "file_path": "/path/to/book.epub",
      "group": "MYGRP",
      "output_dir": "releases",
      "enable_api": true
    }
  ]
}
```

### `config.json`
Exemple de fichier de configuration pour le packaging.

**Options disponibles :**
- `api` : Configuration APIs externes
- `nfo` : Configuration génération NFO
- `rar` : Configuration archives RAR
- `zip` : Configuration archives ZIP
- `validation` : Options de validation
- `sample` : Configuration extraction samples

### `.env.example`
Exemple de variables d'environnement.

**Variables importantes :**
- `DATABASE_URL` : Connexion MySQL (requis)
- `JWT_SECRET_KEY` : Clé secrète JWT (requis)
- `API_KEYS_ENCRYPTION_KEY` : Clé chiffrement API keys (recommandé)
- `FLASK_ENV` : Environnement (development/production)

## Utilisation

1. Copier les fichiers dans le répertoire racine du projet
2. Adapter les valeurs selon votre environnement
3. Utiliser avec les commandes CLI ou API

## Génération

Pour régénérer ces exemples :
```bash
python scripts/generate_examples.py
```
