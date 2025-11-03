# Exemples d'utilisation du CLI enrichi

## Commande pack (simple)

```bash
# Pack eBook simple
python src/packer_cli.py pack book.epub -g MYGRP --type EBOOK

# Pack avec création job en base
python src/packer_cli.py pack book.epub -g MYGRP --type EBOOK --with-job

# Pack TV avec profil
python src/packer_cli.py pack video.mkv -g MYGRP --type TV --release-name "Ma.Release.FRENCH.1080p.WEB-MYGRP" --profile HDTV_1080P

# Sortie JSON
python src/packer_cli.py pack book.epub -g MYGRP --json
```

## Commande batch

```bash
# Batch depuis fichier
python src/packer_cli.py batch --file jobs.json

# Batch depuis stdin
echo '{"jobs": [{"type": "EBOOK", "group": "MYGRP", "file": "book1.epub"}, {"type": "EBOOK", "group": "MYGRP", "file": "book2.epub"}]}' | python src/packer_cli.py batch --stdin

# Exemple fichier jobs.json
cat > jobs.json << EOF
{
  "jobs": [
    {
      "type": "EBOOK",
      "group": "MYGRP",
      "file": "book1.epub",
      "enable_api": true,
      "source": "RETAIL"
    },
    {
      "type": "EBOOK",
      "group": "MYGRP",
      "file": "book2.pdf",
      "enable_api": false
    },
    {
      "type": "TV",
      "group": "MYGRP",
      "file": "video.mkv",
      "release_name": "Ma.Release.FRENCH.1080p.WEB-MYGRP",
      "profile": "HDTV_1080P"
    }
  ]
}
EOF
```

## Commande list-jobs

```bash
# Liste tous les jobs
python src/packer_cli.py list-jobs

# Filtrer par statut
python src/packer_cli.py list-jobs --status completed

# Filtrer par type
python src/packer_cli.py list-jobs --type EBOOK

# Limiter résultats
python src/packer_cli.py list-jobs --limit 10

# Sortie JSON
python src/packer_cli.py list-jobs --json
```

## Commande logs

```bash
# Afficher logs d'un job
python src/packer_cli.py logs <job_id>

# Sortie JSON
python src/packer_cli.py logs <job_id> --json
```

## Commande prefs

```bash
# Récupérer préférence
python src/packer_cli.py prefs get "MYGRP+EBOOK+default"

# Définir préférence depuis valeur JSON
python src/packer_cli.py prefs set "MYGRP+EBOOK+default" --value '{"template_id": 1, "enable_api": true}'

# Définir préférence depuis fichier
python src/packer_cli.py prefs set "MYGRP+EBOOK+default" --file prefs.json

# Définir préférence depuis stdin
echo '{"template_id": 1}' | python src/packer_cli.py prefs set "MYGRP+EBOOK+default"
```

## Commande templates

```bash
# Liste templates
python src/packer_cli.py templates list

# Récupérer template
python src/packer_cli.py templates get 1

# Sortie JSON
python src/packer_cli.py templates list --json
```

## Codes de sortie

- `0` : Succès
- `1` : Erreur générale
- `2` : Erreur validation
- `3` : Erreur fichier/job introuvable
- `130` : Interruption utilisateur (Ctrl+C)
