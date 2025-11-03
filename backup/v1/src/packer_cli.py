#!/usr/bin/env python3
"""
CLI enrichi pour Scene Packer avec batch processing et gestion préférences.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.packaging.docs_packer import pack_docs_release

# Imports locaux
from src.packer import load_config, process_ebook
from src.video import pack_tv_release
from web.app import create_app
from web.database import db
from web.models.job import Job, JobStatus
from web.models.preference import GlobalPreference, UserPreference
from web.models.template import NfoTemplate
from web.models.user import User, UserRole
from web.services.packaging import PackagingService

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure le logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_app_context():
    """Crée le contexte Flask pour accès DB."""
    app = create_app()
    return app.app_context()


def pack_command(args: argparse.Namespace) -> int:
    """Commande pack : packager un fichier."""
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"✗ Erreur: Fichier introuvable: {file_path}", file=sys.stderr)
            return 3

        config = load_config(args.config)

        # Packager selon type
        if args.type == "EBOOK":
            release_name = process_ebook(
                ebook_path=file_path,
                group=args.group,
                output_dir=args.output,
                source_type=args.source,
                url=args.url,
                enable_api=not args.no_api,
                config=config,
                verbose=args.verbose,
                nfo_template_path=args.template,
            )
        elif args.type == "TV":
            if not args.release_name:
                print("✗ Erreur: --release-name requis pour type TV", file=sys.stderr)
                return 2
            release_dir = pack_tv_release(
                input_mkv=file_path,
                release_name=args.release_name,
                link=args.url,
                profile=args.profile,
            )
            release_name = release_dir.name
        elif args.type == "DOCS":
            from src.packaging.docs_packer import pack_docs_release

            release_name = pack_docs_release(
                doc_path=file_path,
                group=args.group,
                output_dir=args.output,
                source_type=args.source,
                url=args.url,
                nfo_template_path=args.template,
                config=config,
            )
        else:
            print(f"✗ Erreur: Type non supporté: {args.type}", file=sys.stderr)
            return 2

        if args.json:
            print(
                json.dumps(
                    {
                        "success": True,
                        "release_name": release_name,
                        "output_dir": str(args.output or "releases"),
                    }
                )
            )
        else:
            print(f"\n✓ Release créée avec succès: {release_name}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"Fichier introuvable: {e}")
        return 3
    except ValueError as e:
        logger.error(f"Erreur validation: {e}")
        return 2
    except RuntimeError as e:
        logger.error(f"Erreur packaging: {e}")
        return 1
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        return 1


def pack_with_job(args: argparse.Namespace) -> int:
    """Commande pack avec création job en base."""
    try:
        with get_app_context():
            # Obtenir utilisateur (admin par défaut en CLI)
            user = User.query.filter_by(role=UserRole.ADMIN).first()
            if not user:
                print(
                    "✗ Erreur: Aucun utilisateur admin trouvé. Exécutez python web/scripts/seed_admin.py",
                    file=sys.stderr,
                )
                return 1

            service = PackagingService(user_id=user.id)

            file_path = Path(args.file)
            if not file_path.exists():
                print(f"✗ Erreur: Fichier introuvable: {file_path}", file=sys.stderr)
                return 3

            if args.type == "EBOOK":
                job = service.pack_ebook(
                    ebook_path=file_path,
                    group=args.group,
                    output_dir=args.output,
                    source_type=args.source,
                    url=args.url,
                    enable_api=not args.no_api,
                    nfo_template_path=args.template,
                    config=load_config(args.config),
                )
            elif args.type == "TV":
                if not args.release_name:
                    print(
                        "✗ Erreur: --release-name requis pour type TV", file=sys.stderr
                    )
                    return 2
                job = service.pack_tv(
                    input_mkv=file_path,
                    release_name=args.release_name,
                    link=args.url,
                    profile=args.profile,
                    output_dir=args.output,
                )
            elif args.type == "DOCS":
                job = service.pack_docs(
                    doc_path=file_path,
                    group=args.group,
                    output_dir=args.output,
                    source_type=args.source,
                    url=args.url,
                    nfo_template_path=args.template,
                    config=load_config(args.config),
                )
            else:
                print(f"✗ Erreur: Type non supporté: {args.type}", file=sys.stderr)
                return 2

            if args.json:
                print(
                    json.dumps(
                        {
                            "success": True,
                            "job_id": job.job_id,
                            "status": job.status.value,
                            "release_name": job.release_name,
                        }
                    )
                )
            else:
                print(f"\n✓ Job créé: {job.job_id}")
                print(f"  Statut: {job.status.value}")
                if job.release_name:
                    print(f"  Release: {job.release_name}")

            return 0

    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        return 1


def batch_command(args: argparse.Namespace) -> int:
    """Commande batch : traitement par lot."""
    try:
        with get_app_context():
            # Obtenir utilisateur
            user = User.query.filter_by(role=UserRole.ADMIN).first()
            if not user:
                print("✗ Erreur: Aucun utilisateur admin trouvé", file=sys.stderr)
                return 1

            service = PackagingService(user_id=user.id)

            # Charger jobs depuis fichier ou stdin
            if args.file:
                with open(args.file, "r") as f:
                    jobs_data = json.load(f)
            else:
                # Lire depuis stdin
                jobs_data = json.load(sys.stdin)

            if "jobs" not in jobs_data:
                print(
                    '✗ Erreur: Format JSON invalide. Attendu: {"jobs": [...]}',
                    file=sys.stderr,
                )
                return 2

            jobs = jobs_data["jobs"]
            total = len(jobs)
            success_count = 0
            failed_count = 0

            results = []

            for i, job_config in enumerate(jobs, 1):
                print(
                    f"\n[{i}/{total}] Traitement job...",
                    file=sys.stderr if not args.json else sys.stdout,
                )

                try:
                    job_type = job_config.get("type", "EBOOK")
                    group = job_config.get("group")
                    file_path = job_config.get("file")

                    if not group or not file_path:
                        raise ValueError("group et file requis")

                    file_path = Path(file_path)
                    if not file_path.exists():
                        raise FileNotFoundError(f"Fichier introuvable: {file_path}")

                    if job_type == "EBOOK":
                        job = service.pack_ebook(
                            ebook_path=file_path,
                            group=group,
                            output_dir=job_config.get("output"),
                            source_type=job_config.get("source"),
                            url=job_config.get("url"),
                            enable_api=job_config.get("enable_api", True),
                            nfo_template_path=job_config.get("template"),
                            config=load_config(args.config),
                        )
                    elif job_type == "TV":
                        release_name = job_config.get("release_name")
                        if not release_name:
                            raise ValueError("release_name requis pour type TV")
                        job = service.pack_tv(
                            input_mkv=file_path,
                            release_name=release_name,
                            link=job_config.get("link"),
                            profile=job_config.get("profile"),
                            output_dir=job_config.get("output"),
                        )
                    elif job_type == "DOCS":
                        job = service.pack_docs(
                            doc_path=file_path,
                            group=group,
                            output_dir=job_config.get("output"),
                            source_type=job_config.get("source"),
                            url=job_config.get("url"),
                            nfo_template_path=job_config.get("template"),
                            config=load_config(args.config),
                        )
                    else:
                        raise ValueError(f"Type non supporté: {job_type}")

                    success_count += 1
                    results.append(
                        {
                            "success": True,
                            "job_id": job.job_id,
                            "release_name": job.release_name,
                        }
                    )

                    if not args.json:
                        print(f"  ✓ Succès: {job.job_id}", file=sys.stderr)

                except Exception as e:
                    failed_count += 1
                    results.append(
                        {
                            "success": False,
                            "error": str(e),
                        }
                    )

                    if not args.json:
                        print(f"  ✗ Échec: {e}", file=sys.stderr)

            if args.json:
                print(
                    json.dumps(
                        {
                            "success": True,
                            "total": total,
                            "success_count": success_count,
                            "failed_count": failed_count,
                            "results": results,
                        }
                    )
                )
            else:
                print(
                    f"\n✓ Batch terminé: {success_count}/{total} succès, {failed_count} échecs"
                )

            return 0 if failed_count == 0 else 1

    except json.JSONDecodeError as e:
        print(f"✗ Erreur: JSON invalide: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        logger.error(f"Erreur batch: {e}", exc_info=True)
        return 1


def list_jobs_command(args: argparse.Namespace) -> int:
    """Commande list-jobs : liste les jobs."""
    try:
        with get_app_context():
            query = Job.query

            # Filtres
            if args.status:
                try:
                    status_enum = JobStatus(args.status)
                    query = query.filter_by(status=status_enum)
                except ValueError:
                    print(f"✗ Erreur: Statut invalide: {args.status}", file=sys.stderr)
                    return 2

            if args.type:
                query = query.filter_by(type=args.type)

            if args.user_id:
                query = query.filter_by(user_id=args.user_id)

            # Limite
            if args.limit:
                query = query.limit(args.limit)

            jobs = query.order_by(Job.created_at.desc()).all()

            if args.json:
                jobs_data = [
                    {
                        "job_id": job.job_id,
                        "status": job.status.value,
                        "type": job.type,
                        "group_name": job.group_name,
                        "release_name": job.release_name,
                        "created_at": job.created_at.isoformat(),
                        "completed_at": (
                            job.completed_at.isoformat() if job.completed_at else None
                        ),
                    }
                    for job in jobs
                ]
                print(json.dumps({"success": True, "jobs": jobs_data}))
            else:
                print(f"\nJobs trouvés: {len(jobs)}\n")
                for job in jobs:
                    status_icon = (
                        "✓"
                        if job.status == JobStatus.COMPLETED
                        else "✗" if job.status == JobStatus.FAILED else "⏳"
                    )
                    print(
                        f"{status_icon} {job.job_id[:8]}... | {job.status.value:10} | {job.type:6} | {job.group_name:15} | {job.release_name or 'N/A'}"
                    )

            return 0

    except Exception as e:
        logger.error(f"Erreur liste jobs: {e}", exc_info=True)
        return 1


def logs_command(args: argparse.Namespace) -> int:
    """Commande logs : affiche les logs d'un job."""
    try:
        with get_app_context():
            job = Job.query.filter_by(job_id=args.job_id).first()

            if not job:
                print(f"✗ Erreur: Job introuvable: {args.job_id}", file=sys.stderr)
                return 3

            from web.models.job import JobLog

            logs = (
                JobLog.query.filter_by(job_id=job.id).order_by(JobLog.timestamp).all()
            )

            if args.json:
                logs_data = [
                    {
                        "level": log.level,
                        "message": log.message,
                        "timestamp": log.timestamp.isoformat(),
                    }
                    for log in logs
                ]
                print(json.dumps({"success": True, "logs": logs_data}))
            else:
                print(f"\nLogs pour job {job.job_id}\n")
                print(f"Statut: {job.status.value}")
                print(f"Type: {job.type}")
                print(f"Groupe: {job.group_name}")
                if job.release_name:
                    print(f"Release: {job.release_name}")
                print("\n" + "=" * 80)

                for log in logs:
                    level_icon = {
                        "INFO": "ℹ",
                        "WARNING": "⚠",
                        "ERROR": "✗",
                        "DEBUG": "🔍",
                    }.get(log.level, "•")
                    print(
                        f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {level_icon} {log.level:7} | {log.message}"
                    )

            return 0

    except Exception as e:
        logger.error(f"Erreur logs: {e}", exc_info=True)
        return 1


def prefs_get_command(args: argparse.Namespace) -> int:
    """Commande prefs get : récupère une préférence."""
    try:
        with get_app_context():
            # Obtenir utilisateur
            user = User.query.filter_by(role=UserRole.ADMIN).first()
            if not user:
                print("✗ Erreur: Aucun utilisateur admin trouvé", file=sys.stderr)
                return 1

            preference_key = args.key

            # Chercher préférence utilisateur
            user_pref = UserPreference.query.filter_by(
                user_id=user.id,
                preference_key=preference_key,
            ).first()

            if user_pref:
                value = user_pref.get_value()
                if args.json:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "key": preference_key,
                                "value": value,
                                "source": "user",
                            }
                        )
                    )
                else:
                    print(f"Préférence utilisateur: {preference_key}")
                    print(json.dumps(value, indent=2))
                return 0

            # Fallback: préférence globale
            global_pref = GlobalPreference.query.filter_by(
                preference_key=preference_key
            ).first()
            if global_pref:
                value = global_pref.get_value()
                if args.json:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "key": preference_key,
                                "value": value,
                                "source": "global",
                            }
                        )
                    )
                else:
                    print(f"Préférence globale: {preference_key}")
                    print(json.dumps(value, indent=2))
                return 0

            print(f"✗ Préférence introuvable: {preference_key}", file=sys.stderr)
            return 3

    except Exception as e:
        logger.error(f"Erreur récupération préférence: {e}", exc_info=True)
        return 1


def prefs_set_command(args: argparse.Namespace) -> int:
    """Commande prefs set : définit une préférence."""
    try:
        with get_app_context():
            # Obtenir utilisateur
            user = User.query.filter_by(role=UserRole.ADMIN).first()
            if not user:
                print("✗ Erreur: Aucun utilisateur admin trouvé", file=sys.stderr)
                return 1

            preference_key = args.key

            # Charger valeur depuis fichier ou stdin
            if args.file:
                with open(args.file, "r") as f:
                    preference_value = json.load(f)
            elif args.value:
                preference_value = json.loads(args.value)
            else:
                preference_value = json.load(sys.stdin)

            # Chercher préférence existante
            user_pref = UserPreference.query.filter_by(
                user_id=user.id,
                preference_key=preference_key,
            ).first()

            if user_pref:
                user_pref.set_value(preference_value)
            else:
                user_pref = UserPreference(
                    user_id=user.id,
                    preference_key=preference_key,
                    preference_value=preference_value,
                )
                db.session.add(user_pref)

            db.session.commit()

            if args.json:
                print(
                    json.dumps({"success": True, "message": "Préférence sauvegardée"})
                )
            else:
                print(f"✓ Préférence sauvegardée: {preference_key}")

            return 0

    except json.JSONDecodeError as e:
        print(f"✗ Erreur: JSON invalide: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        logger.error(f"Erreur sauvegarde préférence: {e}", exc_info=True)
        db.session.rollback()
        return 1


def templates_list_command(args: argparse.Namespace) -> int:
    """Commande templates list : liste les templates."""
    try:
        with get_app_context():
            templates = NfoTemplate.query.all()

            if args.json:
                templates_data = [
                    {
                        "id": t.id,
                        "name": t.name,
                        "description": t.description,
                        "is_default": t.is_default,
                        "created_at": t.created_at.isoformat(),
                    }
                    for t in templates
                ]
                print(json.dumps({"success": True, "templates": templates_data}))
            else:
                print(f"\nTemplates disponibles: {len(templates)}\n")
                for t in templates:
                    default_mark = "⭐" if t.is_default else " "
                    print(
                        f"{default_mark} {t.id:4} | {t.name:30} | {t.description or 'N/A'}"
                    )

            return 0

    except Exception as e:
        logger.error(f"Erreur liste templates: {e}", exc_info=True)
        return 1


def templates_get_command(args: argparse.Namespace) -> int:
    """Commande templates get : récupère un template."""
    try:
        with get_app_context():
            template_id = int(args.template_id)
            template = NfoTemplate.query.get(template_id)

            if not template:
                print(f"✗ Erreur: Template introuvable: {template_id}", file=sys.stderr)
                return 3

            if args.json:
                print(
                    json.dumps(
                        {
                            "success": True,
                            "template": {
                                "id": template.id,
                                "name": template.name,
                                "description": template.description,
                                "content": template.content,
                                "variables": template.get_variables(),
                                "is_default": template.is_default,
                            },
                        }
                    )
                )
            else:
                print(f"\nTemplate: {template.name}")
                print(f"ID: {template.id}")
                print(f"Description: {template.description or 'N/A'}")
                print(f"Défaut: {'Oui' if template.is_default else 'Non'}")
                print(f"\nContenu:\n{template.content}")
                if template.variables:
                    print(
                        f"\nVariables: {json.dumps(template.get_variables(), indent=2)}"
                    )

            return 0

    except ValueError:
        print(f"✗ Erreur: ID invalide: {args.template_id}", file=sys.stderr)
        return 2
    except Exception as e:
        logger.error(f"Erreur récupération template: {e}", exc_info=True)
        return 1


def main():
    """Point d'entrée CLI principal."""
    parser = argparse.ArgumentParser(
        description="Scene Packer CLI - Packaging de releases avec gestion jobs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbose")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument("-c", "--config", type=str, help="Fichier config")

    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Commande pack
    pack_parser = subparsers.add_parser("pack", help="Packager un fichier")
    pack_parser.add_argument("file", type=str, help="Chemin fichier")
    pack_parser.add_argument(
        "-g", "--group", type=str, required=True, help="Groupe Scene"
    )
    pack_parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=["EBOOK", "TV", "DOCS"],
        default="EBOOK",
        help="Type release",
    )
    pack_parser.add_argument("-o", "--output", type=str, help="Dossier sortie")
    pack_parser.add_argument(
        "-s",
        "--source",
        type=str,
        choices=["RETAIL", "SCAN", "HYBRID"],
        help="Type source",
    )
    pack_parser.add_argument("--url", type=str, help="URL release")
    pack_parser.add_argument("--no-api", action="store_true", help="Désactiver APIs")
    pack_parser.add_argument("--template", type=str, help="ID template NFO")
    pack_parser.add_argument(
        "--release-name", type=str, help="Nom release (TV uniquement)"
    )
    pack_parser.add_argument("--profile", type=str, help="Profil (TV uniquement)")
    pack_parser.add_argument(
        "--with-job", action="store_true", help="Créer job en base"
    )

    # Commande batch
    batch_parser = subparsers.add_parser("batch", help="Traitement par lot")
    batch_parser.add_argument("-f", "--file", type=str, help="Fichier JSON jobs")
    batch_parser.add_argument("--stdin", action="store_true", help="Lire depuis stdin")

    # Commande list-jobs
    list_jobs_parser = subparsers.add_parser("list-jobs", help="Liste les jobs")
    list_jobs_parser.add_argument(
        "--status",
        type=str,
        choices=["pending", "running", "completed", "failed"],
        help="Filtrer par statut",
    )
    list_jobs_parser.add_argument("--type", type=str, help="Filtrer par type")
    list_jobs_parser.add_argument("--user-id", type=int, help="Filtrer par utilisateur")
    list_jobs_parser.add_argument("--limit", type=int, help="Limite résultats")

    # Commande logs
    logs_parser = subparsers.add_parser("logs", help="Affiche les logs d'un job")
    logs_parser.add_argument("job_id", type=str, help="ID du job")

    # Sous-commandes prefs
    prefs_parser = subparsers.add_parser("prefs", help="Gestion préférences")
    prefs_subparsers = prefs_parser.add_subparsers(dest="prefs_command")

    prefs_get = prefs_subparsers.add_parser("get", help="Récupère une préférence")
    prefs_get.add_argument("key", type=str, help="Clé préférence")

    prefs_set = prefs_subparsers.add_parser("set", help="Définit une préférence")
    prefs_set.add_argument("key", type=str, help="Clé préférence")
    prefs_set.add_argument("--value", type=str, help="Valeur JSON")
    prefs_set.add_argument("--file", type=str, help="Fichier JSON")

    # Sous-commandes templates
    templates_parser = subparsers.add_parser("templates", help="Gestion templates")
    templates_subparsers = templates_parser.add_subparsers(dest="templates_command")

    templates_list = templates_subparsers.add_parser("list", help="Liste les templates")
    templates_get = templates_subparsers.add_parser("get", help="Récupère un template")
    templates_get.add_argument("template_id", type=str, help="ID du template")

    args = parser.parse_args()

    # Configuration logging
    setup_logging(args.verbose)

    # Exécuter commande
    if args.command == "pack":
        if args.with_job:
            return pack_with_job(args)
        else:
            return pack_command(args)
    elif args.command == "batch":
        return batch_command(args)
    elif args.command == "list-jobs":
        return list_jobs_command(args)
    elif args.command == "logs":
        return logs_command(args)
    elif args.command == "prefs":
        if args.prefs_command == "get":
            return prefs_get_command(args)
        elif args.prefs_command == "set":
            return prefs_set_command(args)
        else:
            parser.print_help()
            return 1
    elif args.command == "templates":
        if args.templates_command == "list":
            return templates_list_command(args)
        elif args.templates_command == "get":
            return templates_get_command(args)
        else:
            parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
