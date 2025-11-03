#!/usr/bin/env python3
"""
Script de seed pour créer des templates NFO par défaut dans la base de données.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
# Le script peut être exécuté depuis différents contextes
script_path = Path(__file__).resolve()

# Trouver le répertoire racine (celui qui contient 'web')
current = script_path.parent
while current != current.parent:
    if (current / "web").exists() and (current / "web" / "app.py").exists():
        root_dir = current
        break
    current = current.parent
else:
    # Fallback : répertoire parent de web
    root_dir = script_path.parent.parent

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from web.app import create_app
from web.database import db
from web.models.template import NfoTemplate
from web.models.user import User, UserRole


def create_default_templates():
    """Crée les templates NFO par défaut."""

    templates = [
        {
            "name": "default_ebook",
            "description": "Template par défaut pour releases EBOOK",
            "content": """┌──────────────────────────────────────────────────────────────────────────────┐
│                           RELEASE INFORMATION                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Title: {{title}}                                                           │
│  Author: {{author}}                                                          │
│  Publisher: {{publisher}}                                                   │
│  Year: {{year}}                                                              │
│  Language: {{language}}                                                      │
│{{#if isbn}}  ISBN: {{isbn}}                                                              │
{{/if}}  Format: {{format}}                                                          │
│                                                                              │
│  Release Name: {{release_name}}                                              │
│  Group: {{group}}                                                            │
│                                                                              │
{{#if url}}│  URL: {{url}}                                                                │
{{/if}}│  Size: {{size}}                                                              │
│  MD5: {{md5}}                                                                │
│  SHA1: {{sha1}}                                                              │
│                                                                              │
│  Note: This release complies with International Ebook Rules 2022            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
""",
            "is_default": True,
        },
        {
            "name": "default_tv",
            "description": "Template par défaut pour releases TV",
            "content": """┌──────────────────────────────────────────────────────────────────────────────┐
│                           RELEASE INFORMATION                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Title: {{title}}                                                           │
│{{#if season}}  Season: {{season}}                                                              │
{{/if}}{{#if episode}}  Episode: {{episode}}                                                              │
{{/if}}{{#if plot}}  Plot: {{plot}}                                                              │
{{/if}}{{#if rating}}  Rating: {{rating}}/10                                                              │
{{/if}}{{#if genre}}  Genre: {{genre}}                                                              │
{{/if}}{{#if network}}  Network: {{network}}                                                              │
{{/if}}│                                                                              │
│  Release Name: {{release_name}}                                              │
│  Group: {{group}}                                                            │
│                                                                              │
│  Video: {{video_codec}} - {{video_resolution}}                               │
│  Audio: {{audio_codec}} - {{audio_channels}}                                │
│  Duration: {{duration}}                                                      │
│  Size: {{size}}                                                              │
│                                                                              │
│  MD5: {{md5}}                                                                │
│  SHA1: {{sha1}}                                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
""",
            "is_default": False,
        },
        {
            "name": "default_docs",
            "description": "Template par défaut pour releases DOCS",
            "content": """┌──────────────────────────────────────────────────────────────────────────────┐
│                           RELEASE INFORMATION                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Title: {{title}}                                                           │
│{{#if author}}  Author: {{author}}                                                          │
{{/if}}{{#if publisher}}  Publisher: {{publisher}}                                                   │
{{/if}}{{#if year}}  Year: {{year}}                                                              │
{{/if}}  Format: {{format}}                                                          │
│                                                                              │
│  Release Name: {{release_name}}                                              │
│  Group: {{group}}                                                            │
│                                                                              │
│  Size: {{size}}                                                              │
│  MD5: {{md5}}                                                                │
│  SHA1: {{sha1}}                                                              │
│                                                                              │
│  Note: This release complies with International Ebook Rules 2022            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
""",
            "is_default": False,
        },
        {
            "name": "minimal",
            "description": "Template minimal simple",
            "content": """{{release_name}}

{{title}}
{{#if author}}by {{author}}{{/if}}
{{#if year}}({{year}}){{/if}}

Group: {{group}}
Size: {{size}}
MD5: {{md5}}
""",
            "is_default": False,
        },
    ]

    app = create_app()

    with app.app_context():
        # Récupérer ou créer utilisateur admin pour attribution
        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        if not admin:
            # Créer admin temporaire si nécessaire
            admin = User(
                username="system",
                email="system@localhost",
                role=UserRole.ADMIN,
            )
            admin.set_password("temp")
            db.session.add(admin)
            db.session.commit()

        created_count = 0
        updated_count = 0

        for template_data in templates:
            # Vérifier si template existe déjà
            existing = NfoTemplate.query.filter_by(name=template_data["name"]).first()

            if existing:
                # Mettre à jour si existe
                existing.description = template_data["description"]
                existing.content = template_data["content"]
                if template_data["is_default"]:
                    # Désactiver autres templates par défaut
                    NfoTemplate.query.filter(
                        NfoTemplate.is_default == True, NfoTemplate.id != existing.id
                    ).update({"is_default": False})
                    existing.is_default = True
                updated_count += 1
                print(f"✓ Template '{template_data['name']}' mis à jour")
            else:
                # Créer nouveau template
                template = NfoTemplate(
                    name=template_data["name"],
                    description=template_data["description"],
                    content=template_data["content"],
                    is_default=template_data["is_default"],
                    created_by=admin.id,
                )

                if template_data["is_default"]:
                    # Désactiver autres templates par défaut
                    NfoTemplate.query.filter_by(is_default=True).update(
                        {"is_default": False}
                    )

                db.session.add(template)
                created_count += 1
                print(f"✓ Template '{template_data['name']}' créé")

        db.session.commit()

        print(
            f"\n✅ {created_count} template(s) créé(s), {updated_count} template(s) mis à jour"
        )


if __name__ == "__main__":
    try:
        create_default_templates()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Erreur: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
