"""
TV/Video API blueprint.
"""

import logging
from pathlib import Path
from typing import Optional

from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from src.exceptions import FileNotFoundError as AppFileNotFoundError
from src.exceptions import (
    PackagingError,
    ValidationError,
)
from src.video import pack_tv_release
from web.schemas import PackTvIn

logger = logging.getLogger(__name__)

tv_bp = Blueprint("tv", __name__)


def _validate_file_path(file_path: str) -> Path:
    """
    Valide et sécurise un chemin de fichier vidéo.

    Args:
        file_path: Chemin fichier à valider

    Returns:
        Path validé

    Raises:
        ValidationError: Si chemin invalide ou non autorisé
        FileNotFoundError: Si fichier introuvable
    """
    try:
        path = Path(file_path).resolve()

        # Protection directory traversal
        upload_folder = current_app.config.get("UPLOAD_FOLDER", Path("uploads"))

        if not str(path).startswith(str(upload_folder.resolve())):
            raise ValidationError(
                f"Chemin fichier non autorisé: {file_path}",
                field="file_path",
                value=file_path,
            )

        if not path.exists():
            raise AppFileNotFoundError(str(path))

        # Vérifier extension vidéo
        allowed_extensions = (".mkv", ".mp4", ".avi", ".mov", ".m4v")
        if path.suffix.lower() not in allowed_extensions:
            raise ValidationError(
                f"Extension non autorisée: {path.suffix}. Extensions autorisées: {', '.join(allowed_extensions)}",
                field="file_path",
                value=str(path),
            )

        return path

    except (ValueError, OSError) as e:
        raise ValidationError(
            f"Chemin fichier invalide: {file_path}",
            field="file_path",
            value=file_path,
        ) from e


@tv_bp.post("/pack")
def tv_pack():
    """Package un fichier vidéo en release TV Scene."""
    try:
        input_path: Optional[Path] = None
        release_name: Optional[str] = None
        link: Optional[str] = None
        profile: Optional[str] = None

        # Gérer multipart/form-data (upload fichier)
        if request.content_type and request.content_type.startswith(
            "multipart/form-data"
        ):
            file = request.files.get("file")
            release_name = request.form.get("release")
            link = request.form.get("link")
            profile = request.form.get("profile")

            if not file or not release_name:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "file et release requis",
                            "error_type": "ValidationError",
                        }
                    ),
                    400,
                )

            # Sauvegarder fichier uploadé
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            upload_folder.mkdir(parents=True, exist_ok=True)
            save_path = upload_folder / file.filename

            # Sécuriser nom fichier
            secure_filename = Path(file.filename).name
            if (
                ".." in secure_filename
                or "/" in secure_filename
                or "\\" in secure_filename
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Nom de fichier invalide",
                            "error_type": "ValidationError",
                        }
                    ),
                    400,
                )

            file.save(save_path)
            input_path = save_path

        else:
            # Gérer JSON
            data = request.get_json() or {}
            payload = PackTvIn().load(data)

            file_path = payload["file_path"]
            release_name = payload["release"]
            link = payload.get("link")
            profile = payload.get("profile")

            input_path = _validate_file_path(file_path)

        # Valider release_name
        if not release_name or len(release_name) < 1 or len(release_name) > 255:
            raise ValidationError(
                "Nom release invalide (doit être entre 1 et 255 caractères)",
                field="release",
                value=release_name,
            )

        # Packager
        out_dir = pack_tv_release(input_path, release_name, link=link, profile=profile)

        return jsonify(
            {
                "success": True,
                "release_path": str(out_dir),
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
        logger.error(f"Erreur TV pack: {e}", exc_info=True)
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
