"""
API v1 blueprint (ebooks, releases, scene rules, groups, config).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from marshmallow import ValidationError as MarshmallowValidationError

from src.exceptions import (
    ApplicationError,
    ConfigurationError,
)
from src.exceptions import FileNotFoundError as AppFileNotFoundError
from src.exceptions import (
    MetadataError,
    PackagingError,
    ValidationError,
)
from src.metadata import (
    MetadataEnricher,
    detect_format,
    extract_epub_metadata,
    extract_mobi_metadata,
    extract_pdf_metadata,
)
from src.packer import process_ebook
from src.scene_rules import (
    get_cached_rule,
    grab_all_rules,
    grab_and_cache_rule,
    grab_rules_list,
    list_cached_rules,
)
from src.utils import generate_release_name, validate_release
from web.app import CONFIG
from web.schemas import (
    ExtractMetadataIn,
    GroupUpdateIn,
    PackEbookIn,
)

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


def _validate_file_path(
    file_path: str, allowed_extensions: Optional[tuple] = None
) -> Path:
    """
    Valide et sécurise un chemin de fichier.

    Args:
        file_path: Chemin fichier à valider
        allowed_extensions: Extensions autorisées (optionnel)

    Returns:
        Path validé

    Raises:
        ValidationError: Si chemin invalide ou non autorisé
        FileNotFoundError: Si fichier introuvable
    """
    try:
        path = Path(file_path).resolve()

        # Protection directory traversal
        if ".." in str(path) or path.is_absolute():
            # Vérifier que le chemin est dans les dossiers autorisés
            upload_folder = current_app.config.get("UPLOAD_FOLDER", Path("uploads"))
            ebooks_folder = current_app.config.get("EBOOKS_FOLDER", Path("ebooks"))

            if not any(
                str(path).startswith(str(folder.resolve()))
                for folder in [upload_folder, ebooks_folder]
            ):
                raise ValidationError(
                    f"Chemin fichier non autorisé: {file_path}",
                    field="file_path",
                    value=file_path,
                )

        if not path.exists():
            raise AppFileNotFoundError(str(path))

        if allowed_extensions and path.suffix.lower() not in allowed_extensions:
            raise ValidationError(
                f"Extension non autorisée: {path.suffix}. Extensions autorisées: {', '.join(allowed_extensions)}",
                field="file_path",
                value=str(path),
            )

        return path

    except (ValueError, OSError) as e:
        raise ValidationError(
            f"Chemin fichier invalide: {file_path}", field="file_path", value=file_path
        ) from e


@api_bp.get("/meta")
def meta_list():
    """Liste tous les eBooks disponibles."""
    try:
        ebooks = []
        ebooks_dir = current_app.config["EBOOKS_FOLDER"]
        allowed_extensions = (".epub", ".pdf", ".mobi", ".azw", ".azw3", ".cbz")

        for ebook_file in ebooks_dir.glob("*"):
            if ebook_file.is_file() and ebook_file.suffix.lower() in allowed_extensions:
                ebooks.append(
                    {
                        "name": ebook_file.name,
                        "path": str(ebook_file),
                        "size": ebook_file.stat().st_size,
                    }
                )

        return jsonify({"success": True, "ebooks": ebooks})

    except Exception as e:
        logger.error(f"Erreur liste ebooks: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.post("/meta")
def meta_extract():
    """Extrait métadonnées depuis un fichier eBook."""
    try:
        data = request.get_json() or {}
        payload = ExtractMetadataIn().load(data)

        file_path = payload["file_path"]
        enable_api = payload.get("enable_api", True)

        # Valider chemin fichier
        ebook_path = _validate_file_path(
            file_path,
            allowed_extensions=(".epub", ".pdf", ".mobi", ".azw", ".azw3", ".cbz"),
        )

        # Détecter format
        format_type = detect_format(ebook_path)
        if not format_type:
            format_type = (
                ebook_path.suffix[1:].lower() if ebook_path.suffix else "unknown"
            )

        # Extraire métadonnées selon format
        format_lower = format_type.lower()
        if format_lower == "epub":
            metadata = extract_epub_metadata(ebook_path)
        elif format_lower in ("mobi", "azw", "azw3"):
            metadata = extract_mobi_metadata(ebook_path)
        elif format_lower == "pdf":
            metadata = extract_pdf_metadata(ebook_path)
        else:
            metadata = {
                "title": ebook_path.stem,
                "author": None,
                "publisher": None,
                "language": "en",
                "year": None,
                "isbn": None,
                "format": format_type.upper(),
                "api_sources": [],
            }

        # Enrichissement API si activé
        if enable_api:
            api_config = CONFIG.get("api", {})
            enricher = MetadataEnricher(
                enable_googlebooks=api_config.get("enable_googlebooks", True),
                enable_openlibrary=api_config.get("enable_openlibrary", True),
                timeout=api_config.get("timeout", 10),
                rate_limit_delay=api_config.get("rate_limit_delay", 0.5),
            )
            metadata = enricher.enrich(metadata)

        return jsonify({"success": True, "metadata": metadata, "format": format_type})

    except MarshmallowValidationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Données de validation invalides",
                    "error_type": "ValidationError",
                    "details": e.messages,
                }
            ),
            400,
        )
    except (ValidationError, AppFileNotFoundError) as e:
        return jsonify(e.to_dict()), 400 if isinstance(e, ValidationError) else 404
    except Exception as e:
        logger.error(f"Erreur extraction métadonnées: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "MetadataError",
                }
            ),
            500,
        )


@api_bp.post("/pack")
def pack():
    """Package un eBook en release Scene."""
    try:
        data = request.get_json() or {}
        payload = PackEbookIn().load(data)

        file_path = payload["file_path"]
        group = payload["group"]
        source = payload.get("source")
        url = payload.get("url")
        enable_api = payload.get("enable_api", True)
        nfo_template = payload.get("nfo_template")

        # Valider chemin fichier
        ebook_path = _validate_file_path(
            file_path,
            allowed_extensions=(".epub", ".pdf", ".mobi", ".azw", ".azw3", ".cbz"),
        )

        # Packager
        release_name = process_ebook(
            ebook_path=ebook_path,
            group=group,
            output_dir=current_app.config["RELEASES_FOLDER"],
            source_type=source,
            url=url,
            enable_api=enable_api,
            config=CONFIG,
            verbose=False,
            nfo_template_path=nfo_template,
        )

        release_path = current_app.config["RELEASES_FOLDER"] / release_name

        return jsonify(
            {
                "success": True,
                "release_path": str(release_path),
                "release_name": release_name,
            }
        )

    except MarshmallowValidationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Données de validation invalides",
                    "error_type": "ValidationError",
                    "details": e.messages,
                }
            ),
            400,
        )
    except (ValidationError, AppFileNotFoundError) as e:
        return jsonify(e.to_dict()), 400 if isinstance(e, ValidationError) else 404
    except PackagingError as e:
        return jsonify(e.to_dict()), 500
    except Exception as e:
        logger.error(f"Erreur packaging: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "PackagingError",
                }
            ),
            500,
        )


@api_bp.get("/releases")
def releases_list():
    """Liste toutes les releases créées."""
    try:
        cache_ext = current_app.extensions.get("cache")
        cached = None
        if cache_ext and hasattr(cache_ext, "get"):
            try:
                cached = cache_ext.get("releases_list")
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.debug(f"Erreur récupération cache: {e}")
                cached = None
        if cached:
            return jsonify({"success": True, "releases": cached})

        releases = []
        releases_dir = current_app.config["RELEASES_FOLDER"]

        for release_dir in releases_dir.iterdir():
            if release_dir.is_dir():
                release_name = release_dir.name
                zip_files = list(release_dir.glob("*.ZIP")) + list(
                    release_dir.glob("*.Z*")
                )
                rar_files = list(release_dir.glob("*.rar")) + list(
                    release_dir.glob("*.r*")
                )
                nfo_files = list(release_dir.glob("*.nfo"))
                sfv_files = list(release_dir.glob("*.sfv"))
                total_size = sum(
                    f.stat().st_size for f in release_dir.rglob("*") if f.is_file()
                )
                releases.append(
                    {
                        "name": release_name,
                        "path": str(release_dir),
                        "has_nfo": len(nfo_files) > 0,
                        "has_sfv": len(sfv_files) > 0,
                        "zip_volumes": len(zip_files),
                        "rar_volumes": len(rar_files),
                        "size": total_size,
                        "created_at": release_dir.stat().st_mtime,
                    }
                )

        releases.sort(key=lambda x: x["created_at"], reverse=True)
        if cache_ext and hasattr(cache_ext, "set"):
            try:
                cache_ext.set("releases_list", releases, timeout=60)
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.debug(f"Erreur mise en cache: {e}")
                pass
        return jsonify({"success": True, "releases": releases})

    except Exception as e:
        logger.error(f"Erreur liste releases: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.get("/releases/<release_name>/validate")
def release_validate(release_name: str):
    """Valide une release."""
    try:
        release_dir = current_app.config["RELEASES_FOLDER"] / release_name

        if not release_dir.exists():
            raise AppFileNotFoundError(str(release_dir))

        validation_config = CONFIG.get("validation", {})
        is_valid, errors = validate_release(
            release_dir,
            release_name,
            verbose=False,
            config=validation_config,
        )

        return jsonify(
            {
                "success": True,
                "valid": is_valid,
                "errors": errors,
            }
        )

    except AppFileNotFoundError as e:
        return jsonify(e.to_dict()), 404
    except Exception as e:
        logger.error(f"Erreur validation release: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "ValidationError",
                }
            ),
            500,
        )


@api_bp.get("/rules")
def rules_list():
    """Liste toutes les règles Scene disponibles."""
    try:
        rules = grab_rules_list()
        return jsonify({"success": True, "rules": rules})

    except Exception as e:
        logger.error(f"Erreur liste règles: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.get("/rules/cached")
def rules_cached_list():
    """Liste toutes les règles Scene en cache."""
    try:
        cached_rules = list_cached_rules()
        return jsonify({"success": True, "cached_rules": cached_rules})

    except Exception as e:
        logger.error(f"Erreur liste règles cache: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.get("/rules/<rule_name>")
def rule_get(rule_name: str):
    """Récupère une règle Scene spécifique."""
    try:
        year = request.args.get("year", "2022")
        rule_content = get_cached_rule(rule_name, year)

        if not rule_content:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Règle introuvable: {rule_name} ({year})",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        return jsonify(
            {
                "success": True,
                "rule_name": rule_name,
                "year": year,
                "content": rule_content,
            }
        )

    except Exception as e:
        logger.error(f"Erreur récupération règle: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.post("/rules/<rule_name>/cache")
def rule_cache(rule_name: str):
    """Cache une règle Scene depuis scenerules.org."""
    try:
        data = request.get_json() or {}
        url = data.get("url")
        year = data.get("year", "2022")

        if not url:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "URL requise pour cache règle",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        cached_path = grab_and_cache_rule(rule_name, url, year)

        if not cached_path:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Impossible de cacher règle: {rule_name}",
                        "error_type": "IOError",
                    }
                ),
                500,
            )

        return jsonify(
            {
                "success": True,
                "rule_name": rule_name,
                "year": year,
                "cached_path": str(cached_path),
            }
        )

    except Exception as e:
        logger.error(f"Erreur cache règle: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.get("/groups")
def groups_list():
    """Liste tous les groupes Scene configurés."""
    try:
        groups_file = Path("config/groups.json")

        if not groups_file.exists():
            return jsonify({"success": True, "groups": [], "last": None})

        with open(groups_file, "r", encoding="utf-8") as f:
            groups_data = json.load(f)

        return jsonify(
            {
                "success": True,
                "groups": groups_data.get("groups", []),
                "last": groups_data.get("last"),
            }
        )

    except Exception as e:
        logger.error(f"Erreur liste groupes: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.post("/groups")
def groups_add():
    """Ajoute un groupe Scene."""
    try:
        data = request.get_json() or {}
        payload = GroupUpdateIn().load(data)
        group = payload["group"]

        groups_file = Path("config/groups.json")
        groups_data = {"groups": [], "last": None}

        if groups_file.exists():
            with open(groups_file, "r", encoding="utf-8") as f:
                groups_data = json.load(f)

        if group not in groups_data.get("groups", []):
            groups_data.setdefault("groups", []).append(group)

        groups_data["last"] = group

        groups_file.parent.mkdir(parents=True, exist_ok=True)
        with open(groups_file, "w", encoding="utf-8") as f:
            json.dump(groups_data, f, indent=2)

        return jsonify(
            {
                "success": True,
                "groups": groups_data["groups"],
                "last": groups_data["last"],
            }
        )

    except MarshmallowValidationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Données de validation invalides",
                    "error_type": "ValidationError",
                    "details": e.messages,
                }
            ),
            400,
        )
    except Exception as e:
        logger.error(f"Erreur ajout groupe: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.post("/groups/last")
def groups_set_last():
    """Définit le dernier groupe utilisé."""
    try:
        data = request.get_json() or {}
        payload = GroupUpdateIn().load(data)
        group = payload["group"]

        groups_file = Path("config/groups.json")
        groups_data = {"groups": [], "last": None}

        if groups_file.exists():
            with open(groups_file, "r", encoding="utf-8") as f:
                groups_data = json.load(f)

        if group not in groups_data.get("groups", []):
            groups_data.setdefault("groups", []).append(group)

        groups_data["last"] = group

        groups_file.parent.mkdir(parents=True, exist_ok=True)
        with open(groups_file, "w", encoding="utf-8") as f:
            json.dump(groups_data, f, indent=2)

        return jsonify(
            {
                "success": True,
                "last": groups_data["last"],
            }
        )

    except MarshmallowValidationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Données de validation invalides",
                    "error_type": "ValidationError",
                    "details": e.messages,
                }
            ),
            400,
        )
    except Exception as e:
        logger.error(f"Erreur définition groupe: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.get("/config")
def config_get():
    """Récupère la configuration actuelle."""
    try:
        return jsonify({"success": True, "config": CONFIG})

    except Exception as e:
        logger.error(f"Erreur chargement config: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "IOError",
                }
            ),
            500,
        )


@api_bp.post("/config")
def config_save():
    """Sauvegarde la configuration."""
    try:
        import yaml

        data = request.get_json() or {}

        # Validation basique
        if not isinstance(data, dict):
            raise ValidationError("Configuration doit être un objet JSON")

        config_file = Path("config/config.yaml")
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        # Recharger config
        from web.app import load_config

        global CONFIG
        CONFIG = load_config()

        return jsonify({"success": True, "config": CONFIG})

    except Exception as e:
        logger.error(f"Erreur sauvegarde config: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "error_type": "ConfigurationError",
                }
            ),
            500,
        )


@api_bp.get("/nfo-templates")
def nfo_templates_list():
    """Liste tous les templates NFO disponibles."""
    try:
        base = Path("templates/nfo")
        base.mkdir(parents=True, exist_ok=True)
        items = []
        for f in base.glob("*.txt"):
            items.append({"name": f.stem, "path": str(f), "size": f.stat().st_size})
        # Ajouter default s'il n'est pas dans le dossier nfo
        default_path = Path("templates/nfo_template.txt")
        if default_path.exists():
            items.insert(
                0,
                {
                    "name": "default",
                    "path": str(default_path),
                    "size": default_path.stat().st_size,
                },
            )
        return jsonify({"success": True, "templates": items})
    except Exception as e:
        logger.error(f"Erreur liste templates NFO: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )


@api_bp.get("/nfo-templates/<name>")
def nfo_templates_get(name: str):
    """Récupère le contenu d'un template NFO."""
    try:
        if name == "default":
            path = Path("templates/nfo_template.txt")
        else:
            path = Path("templates/nfo") / f"{name}.txt"
        if not path.exists():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Template introuvable",
                        "error_type": "IOError",
                    }
                ),
                404,
            )
        return jsonify(
            {"success": True, "name": name, "content": path.read_text(encoding="utf-8")}
        )
    except Exception as e:
        logger.error(f"Erreur lecture template NFO: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )


@api_bp.post("/nfo-templates")
def nfo_templates_save():
    """Sauvegarde un template NFO."""
    try:
        data = request.get_json() or {}
        name = data.get("name")
        content = data.get("content")
        if not name or not content:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "name et content requis",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )
        if name == "default":
            path = Path("templates/nfo_template.txt")
        else:
            base = Path("templates/nfo")
            base.mkdir(parents=True, exist_ok=True)
            path = base / f"{name}.txt"
        path.write_text(content, encoding="utf-8")
        return jsonify({"success": True, "name": name, "path": str(path)})
    except Exception as e:
        logger.error(f"Erreur sauvegarde template NFO: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )


@api_bp.delete("/nfo-templates/<name>")
def nfo_templates_delete(name: str):
    """Supprime un template NFO."""
    try:
        if name == "default":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Suppression du template par défaut interdite",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )
        path = Path("templates/nfo") / f"{name}.txt"
        if not path.exists():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Template introuvable",
                        "error_type": "IOError",
                    }
                ),
                404,
            )
        path.unlink()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Erreur suppression template NFO: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )


@api_bp.get("/prefs")
def prefs_get():
    """Récupère les préférences utilisateur."""
    try:
        p = Path("config/prefs.json")
        if p.exists():
            return jsonify(
                {"success": True, **json.loads(p.read_text(encoding="utf-8"))}
            )
        return jsonify({"success": True, "last_group": None, "last_nfo_template": None})
    except Exception as e:
        logger.error(f"Erreur chargement prefs: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )


@api_bp.post("/prefs")
def prefs_save():
    """Sauvegarde les préférences utilisateur."""
    try:
        data = request.get_json() or {}
        allowed = {k: data.get(k) for k in ("last_group", "last_nfo_template")}
        p = Path("config/prefs.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(allowed, indent=2), encoding="utf-8")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Erreur sauvegarde prefs: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )


@api_bp.post("/metrics")
def metrics_collect():
    """Collecte Web Vitals (INP/TTFB/CLS) côté client."""
    try:
        data = request.get_json() or {}
        path = Path("cache/webvitals.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            import json as _json
            import time

            record = {"ts": int(time.time()), **data}
            f.write(_json.dumps(record) + "\n")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Erreur collecte metrics: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )


@api_bp.get("/releases/<release_name>/download/<file_type>")
def releases_download(release_name: str, file_type: str):
    """Télécharge un fichier depuis une release."""
    try:
        release_dir = current_app.config["RELEASES_FOLDER"] / release_name
        if not release_dir.exists():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Release introuvable",
                        "error_type": "IOError",
                    }
                ),
                404,
            )
        if file_type == "nfo":
            files = list(release_dir.glob("*.nfo"))
        elif file_type == "sfv":
            files = list(release_dir.glob("*.sfv"))
        elif file_type == "rar":
            files = list(release_dir.glob("*.rar"))
        elif file_type == "zip":
            files = list(release_dir.glob("*.ZIP"))
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Type fichier invalide",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )
        if not files:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Fichier {file_type} introuvable",
                        "error_type": "IOError",
                    }
                ),
                404,
            )
        return send_from_directory(release_dir, files[0].name, as_attachment=True)
    except Exception as e:
        logger.error(f"Erreur téléchargement: {e}", exc_info=True)
        return (
            jsonify({"success": False, "error": str(e), "error_type": "IOError"}),
            500,
        )
