"""
Blueprint pour le wizard de packaging (12 étapes).
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from src.metadata import (
    MetadataEnricher,
    detect_format,
    extract_epub_metadata,
    extract_mobi_metadata,
    extract_pdf_metadata,
)
from src.packaging.docs_packer import extract_docs_metadata
from src.video.media_info import probe_media_info
from web.app import CONFIG
from web.auth import operator_or_admin_required
from web.database import db
from web.helpers import get_current_user_id
from web.models.job import Job, JobStatus
from web.schemas.wizard import WizardPackRequestSchema, WizardStepValidateSchema
from web.services.packaging import PackagingService

logger = logging.getLogger(__name__)

wizard_bp = Blueprint("wizard", __name__)


def _handle_file_source(files_config: Dict[str, Any]) -> tuple[Path, Optional[tuple]]:
    """
    Gère la source du fichier (local ou distant).

    Args:
        files_config: Configuration fichiers depuis payload

    Returns:
        Tuple (file_path, error_response) - error_response est None si succès, sinon (jsonify_response, status_code)
    """
    file_source = files_config.get("source", "local")

    if file_source == "local":
        file_path = Path(files_config.get("path"))
        if not file_path.exists():
            return None, (
                jsonify(
                    {
                        "success": False,
                        "error": "Fichier introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )
        return file_path, None

    elif file_source == "remote":
        url = files_config.get("url")
        if not url:
            return None, (
                jsonify(
                    {
                        "success": False,
                        "error": "URL requise pour fichier distant",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Télécharger fichier distant
        temp_job_id = str(uuid.uuid4())
        try:
            file_path = _download_remote_file(url, temp_job_id)
            return file_path, None
        except Exception as e:
            return None, (
                jsonify(
                    {
                        "success": False,
                        "error": str(e),
                        "error_type": "DownloadError",
                    }
                ),
                500,
            )

    else:
        return None, (
            jsonify(
                {
                    "success": False,
                    "error": "Source fichier invalide",
                    "error_type": "ValidationError",
                }
            ),
            400,
        )


def _extract_ebook_metadata(file_path: Path, use_apis: bool) -> Dict[str, Any]:
    """
    Extrait et enrichit métadonnées pour eBook.

    Args:
        file_path: Chemin fichier eBook
        use_apis: Activer enrichissement APIs

    Returns:
        Dictionnaire métadonnées enrichies
    """
    metadata = {}
    format_type = detect_format(file_path)

    if format_type:
        if format_type.lower() == "epub":
            metadata = extract_epub_metadata(file_path)
        elif format_type.lower() in ("mobi", "azw", "azw3"):
            metadata = extract_mobi_metadata(file_path)
        elif format_type.lower() == "pdf":
            metadata = extract_pdf_metadata(file_path)

    # Enrichissement API si activé
    if use_apis:
        api_config = CONFIG.get("api", {})
        enricher = MetadataEnricher(
            enable_googlebooks=api_config.get("enable_googlebooks", True),
            enable_openlibrary=api_config.get("enable_openlibrary", True),
            timeout=api_config.get("timeout", 10),
            rate_limit_delay=api_config.get("rate_limit_delay", 0.5),
        )
        metadata = enricher.enrich(metadata)

    return metadata


def _pack_by_type(
    packaging_service: PackagingService,
    job_type: str,
    file_path: Path,
    group: str,
    payload: Dict[str, Any],
    use_apis: bool,
    use_mediainfo: bool,
) -> tuple[Optional[Job], Optional[tuple]]:
    """
    Lance le packaging selon le type de release.

    Args:
        packaging_service: Service de packaging
        job_type: Type de release (EBOOK/TV/DOCS)
        file_path: Chemin fichier à packager
        group: Groupe Scene
        payload: Payload complet depuis requête
        use_apis: Activer enrichissement APIs
        use_mediainfo: Activer MediaInfo

    Returns:
        Tuple (job, error_response) - error_response est None si succès, sinon (jsonify_response, status_code)
    """
    from flask import current_app

    if job_type == "EBOOK":
        # Extraction métadonnées
        metadata = _extract_ebook_metadata(file_path, use_apis)

        # Fusion avec métadonnées fournies
        provided_metadata = payload.get("metadata", {})
        metadata.update(provided_metadata)

        # Packager eBook
        job = packaging_service.pack_ebook(
            ebook_path=file_path,
            group=group,
            output_dir=current_app.config["RELEASES_FOLDER"],
            source_type=payload.get("source_type"),
            url=payload.get("url"),
            enable_api=use_apis,
            nfo_template_path=payload.get("template_id"),
            config=CONFIG,
        )
        return job, None

    elif job_type == "TV":
        # MediaInfo si activé
        if use_mediainfo:
            try:
                media_info = probe_media_info(file_path)
            except Exception as e:
                logger.warning(f"Erreur MediaInfo: {e}")

        # Packager TV
        release_name = payload.get("release_name")
        if not release_name:
            return None, (
                jsonify(
                    {
                        "success": False,
                        "error": "Nom de release requis pour type TV",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        job = packaging_service.pack_tv(
            input_mkv=file_path,
            release_name=release_name,
            link=payload.get("link"),
            profile=payload.get("profile"),
            output_dir=current_app.config["RELEASES_FOLDER"],
            enable_api=use_apis,
        )
        return job, None

    elif job_type == "DOCS":
        # Extraction métadonnées DOCS
        metadata = extract_docs_metadata(file_path)

        # Fusion avec métadonnées fournies
        provided_metadata = payload.get("metadata", {})
        metadata.update(provided_metadata)

        # Packager DOCS
        job = packaging_service.pack_docs(
            doc_path=file_path,
            group=group,
            output_dir=current_app.config["RELEASES_FOLDER"],
            source_type=payload.get("source_type"),
            url=payload.get("url"),
            nfo_template_path=payload.get("template_id"),
            config=CONFIG,
        )
        return job, None

    else:
        return None, (
            jsonify(
                {
                    "success": False,
                    "error": f"Type de release non supporté: {job_type}",
                    "error_type": "ValidationError",
                }
            ),
            400,
        )


def _download_remote_file(url: str, job_id: str) -> Path:
    """
    Télécharge un fichier distant et le sauvegarde localement.

    Args:
        url: URL du fichier à télécharger
        job_id: ID du job (pour dossier temporaire)

    Returns:
        Chemin du fichier téléchargé

    Raises:
        ValueError: Si URL invalide ou téléchargement échoué
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"URL invalide: {url}")

        # Créer dossier temporaire pour ce job
        downloads_dir = (
            Path(current_app.config.get("UPLOAD_FOLDER", "uploads"))
            / "downloads"
            / job_id
        )
        downloads_dir.mkdir(parents=True, exist_ok=True)

        # Télécharger fichier
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        # Extraire nom fichier depuis URL ou Content-Disposition
        filename = Path(parsed.path).name or "downloaded_file"
        if "Content-Disposition" in response.headers:
            import re

            match = re.search(
                r'filename="?([^"]+)"?', response.headers["Content-Disposition"]
            )
            if match:
                filename = match.group(1)

        file_path = downloads_dir / filename

        # Sauvegarder fichier
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Fichier téléchargé: {url} -> {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Erreur téléchargement fichier distant: {e}", exc_info=True)
        raise ValueError(f"Erreur téléchargement: {str(e)}") from e


@wizard_bp.post("/step/validate")
@jwt_required()
@operator_or_admin_required
def validate_step():
    """
    Valide les données d'une étape du wizard.

    POST /api/wizard/step/validate
    Body: {"step": 1, "data": {...}}

    Returns:
        Résultat de validation
    """
    try:
        data = request.get_json() or {}
        schema = WizardStepValidateSchema()
        payload = schema.load(data)

        step = payload["step"]
        step_data = payload["data"]

        # Validation selon étape
        errors = []

        if step == 1:  # Nom groupe
            group = step_data.get("group", "").strip()
            if not group:
                errors.append(
                    {"field": "group", "message": "Le nom du groupe est requis"}
                )
            elif len(group) > 100:
                errors.append(
                    {
                        "field": "group",
                        "message": "Le nom du groupe ne peut pas dépasser 100 caractères",
                    }
                )

        elif step == 2:  # Type release
            release_type = step_data.get("type")
            if release_type not in ["TV", "EBOOK", "DOCS"]:
                errors.append({"field": "type", "message": "Type de release invalide"})

        elif step == 4:  # Fichiers
            source = step_data.get("source")  # 'local' ou 'remote'
            if source == "local":
                file_path = step_data.get("path")
                if not file_path:
                    errors.append({"field": "path", "message": "Chemin fichier requis"})
            elif source == "remote":
                url = step_data.get("url")
                if not url:
                    errors.append({"field": "url", "message": "URL requise"})

        if errors:
            return (
                jsonify(
                    {
                        "success": False,
                        "valid": False,
                        "errors": errors,
                    }
                ),
                400,
            )

        return (
            jsonify(
                {
                    "success": True,
                    "valid": True,
                }
            ),
            200,
        )

    except ValidationError as e:
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
        logger.error(f"Erreur validation étape: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la validation",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@wizard_bp.post("/pack")
@jwt_required()
@operator_or_admin_required
def pack():
    """
    Lance le packaging synchrone via le wizard.

    POST /api/wizard/pack
    Body: {
        "group": "MYGRP",
        "type": "EBOOK",
        "rules": [...],
        "files": {"source": "local", "path": "..."},
        "metadata": {...},
        "enrichment": {"use_mediainfo": true, "use_apis": true},
        "template_id": "...",
        "export": {...}
    }

    Returns:
        Job créé avec statut
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}

        schema = WizardPackRequestSchema()
        payload = schema.load(data)

        # Créer service packaging
        packaging_service = PackagingService(user_id=current_user_id)

        # Gérer fichiers (local ou distant)
        group = payload["group"]
        job_type = payload["type"]
        files_config = payload.get("files", {})

        file_path, error_response = _handle_file_source(files_config)
        if error_response:
            return error_response[0], error_response[1]

        # Enrichissement métadonnées
        enrichment_config = payload.get("enrichment", {})
        use_mediainfo = enrichment_config.get("use_mediainfo", False)
        use_apis = enrichment_config.get("use_apis", True)

        # Packager selon type
        job, error_response = _pack_by_type(
            packaging_service=packaging_service,
            job_type=job_type,
            file_path=file_path,
            group=group,
            payload=payload,
            use_apis=use_apis,
            use_mediainfo=use_mediainfo,
        )

        if error_response:
            return error_response[0], error_response[1]

        # Serialization
        from web.schemas.job import JobResponseSchema

        schema = JobResponseSchema()
        job_data = schema.dump(job)

        return (
            jsonify(
                {
                    "success": True,
                    "job": job_data,
                }
            ),
            200,
        )

    except ValidationError as e:
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
        logger.error(f"Erreur packaging wizard: {e}", exc_info=True)
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


@wizard_bp.get("/preferences")
@jwt_required()
@operator_or_admin_required
def get_preferences():
    """
    Récupère les préférences utilisateur pour le wizard.

    GET /api/wizard/preferences?key=group+type+rules+template

    Returns:
        Préférences utilisateur ou globales (fallback)
    """
    try:
        current_user_id = get_current_user_id()
        preference_key = request.args.get("key")

        from web.models.preference import GlobalPreference, UserPreference

        # Chercher préférence utilisateur
        user_pref = (
            UserPreference.query.filter_by(
                user_id=current_user_id,
                preference_key=preference_key,
            ).first()
            if preference_key
            else None
        )

        if user_pref:
            return (
                jsonify(
                    {
                        "success": True,
                        "preference": {
                            "key": user_pref.preference_key,
                            "value": user_pref.get_value(),
                            "source": "user",
                        },
                    }
                ),
                200,
            )

        # Fallback: préférence globale
        if preference_key:
            global_pref = GlobalPreference.query.filter_by(
                preference_key=preference_key,
            ).first()

            if global_pref:
                return (
                    jsonify(
                        {
                            "success": True,
                            "preference": {
                                "key": global_pref.preference_key,
                                "value": global_pref.get_value(),
                                "source": "global",
                            },
                        }
                    ),
                    200,
                )

        # Aucune préférence trouvée
        return (
            jsonify(
                {
                    "success": True,
                    "preference": None,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération préférences: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des préférences",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@wizard_bp.post("/preferences")
@jwt_required()
@operator_or_admin_required
def save_preferences():
    """
    Sauvegarde les préférences utilisateur.

    POST /api/wizard/preferences
    Body: {"key": "...", "value": {...}}

    Returns:
        Confirmation sauvegarde
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}

        preference_key = data.get("key")
        preference_value = data.get("value")

        if not preference_key or not isinstance(preference_value, dict):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Clé et valeur requises",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        from web.models.preference import UserPreference

        # Chercher préférence existante
        user_pref = UserPreference.query.filter_by(
            user_id=current_user_id,
            preference_key=preference_key,
        ).first()

        if user_pref:
            user_pref.set_value(preference_value)
        else:
            user_pref = UserPreference(
                user_id=current_user_id,
                preference_key=preference_key,
                preference_value=preference_value,
            )
            db.session.add(user_pref)

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Préférences sauvegardées",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur sauvegarde préférences: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la sauvegarde des préférences",
                    "error_type": "ServerError",
                }
            ),
            500,
        )
