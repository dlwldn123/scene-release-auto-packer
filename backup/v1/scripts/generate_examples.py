#!/usr/bin/env python3
"""
Script de génération d'exemples de configuration.

Crée des fichiers JSON d'exemple pour batch processing et configuration.
"""

import json
from pathlib import Path


def create_batch_example():
    """Crée un exemple de fichier batch pour CLI."""
    example = {
        "jobs": [
            {
                "type": "EBOOK",
                "file_path": "/path/to/book.epub",
                "group": "MYGRP",
                "output_dir": "releases",
                "enable_api": True,
                "nfo_template": None,
            },
            {
                "type": "DOCS",
                "file_path": "/path/to/document.pdf",
                "group": "MYGRP",
                "output_dir": "releases",
                "source_type": "RETAIL",
                "nfo_template": None,
            },
            {
                "type": "TV",
                "file_path": "/path/to/video.mkv",
                "release_name": "Series.Name.S01E01.720p.HDTV.x264-GROUP",
                "group": "GROUP",
                "link": "https://example.com/release",
                "enable_api": True,
                "profile": "HDTV_720P",
            },
        ]
    }

    output_file = Path("examples/batch_jobs.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(example, f, indent=2, ensure_ascii=False)

    print(f"✓ Exemple batch créé: {output_file}")


def create_config_example():
    """Crée un exemple de fichier de configuration."""
    example = {
        "api": {
            "enable_googlebooks": True,
            "enable_openlibrary": True,
            "rate_limit_delay": 0.5,
            "timeout": 10,
        },
        "nfo": {"ascii_art": True, "max_width": 80, "template_path": None},
        "rar": {"create_for_zip": True, "method": 0},
        "zip": {"allowed_sizes": [5000000, 10000000], "use_83_rule": True},
        "validation": {
            "check_naming": True,
            "check_nfo": True,
            "check_rar": True,
            "check_sample": True,
            "check_sfv": True,
        },
        "sample": {
            "pdf": {"amount": 2, "type": "pages"},
            "epub": {"amount": 1, "type": "chapter"},
        },
    }

    output_file = Path("examples/config.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(example, f, indent=2, ensure_ascii=False)

    print(f"✓ Exemple config créé: {output_file}")


def create_env_example():
    """Crée un exemple de fichier .env."""
    example = """# Configuration MySQL
DATABASE_URL=mysql+pymysql://packer:packer@localhost:3306/packer

# Sécurité
JWT_SECRET_KEY=change-this-secret-key-in-production-use-strong-random-key
API_KEYS_ENCRYPTION_KEY=generate-with-openssl-rand-hex-32

# Environnement
FLASK_ENV=development

# Chemins
RELEASES_FOLDER=releases
UPLOADS_FOLDER=uploads
LOGS_FOLDER=logs
"""

    output_file = Path("examples/.env.example")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(example)

    print(f"✓ Exemple .env créé: {output_file}")


def main():
    print("Génération d'exemples de configuration...\n")

    create_batch_example()
    create_config_example()
    create_env_example()

    print("\n✅ Tous les exemples ont été créés dans le dossier examples/")


if __name__ == "__main__":
    main()
