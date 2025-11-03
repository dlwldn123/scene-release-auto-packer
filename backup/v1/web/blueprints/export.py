"""
Blueprint pour l'export FTP/SFTP manuel.
"""

import logging
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from web.auth import operator_or_admin_required
from web.database import db
from web.models.destination import Destination
from web.models.job import Job
from web.services.ftp_upload import FtpUploadService

logger = logging.getLogger(__name__)

export_bp = Blueprint("export", __name__)


@export_bp.post("/jobs/<job_id>/ftp")
@jwt_required()
@operator_or_admin_required
def export_job_ftp(job_id: str):
    """
    Upload manuel FTP pour un job.

    POST /api/export/jobs/<job_id>/ftp
    Body: {"destination_id": 1}

    Returns:
        Résultat upload
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        destination_id = data.get("destination_id")
        if not destination_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "destination_id requis",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Vérifier job existe et appartient à l'utilisateur (avec eager loading)
        from sqlalchemy.orm import joinedload

        job = (
            Job.query.options(joinedload(Job.artifacts))
            .filter_by(job_id=job_id)
            .first()
        )

        if not job:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Job introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        claims = get_jwt()
        user_role = claims.get("role")
        if user_role != "admin" and job.user_id != current_user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        # Vérifier destination existe
        destination = Destination.query.get(destination_id)
        if not destination:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        if destination.type != "ftp":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination n'est pas de type FTP",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Collecter fichiers à uploader (artifacts déjà chargés via eager loading)
        release_dir = current_app.config["RELEASES_FOLDER"] / job.release_name
        files_to_upload = []

        for artifact in job.artifacts:
            file_path = release_dir / artifact.file_path
            if file_path.exists():
                files_to_upload.append(file_path)

        if not files_to_upload:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Aucun fichier à uploader",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Upload
        upload_service = FtpUploadService(job_id=job.id)
        success, message = upload_service.upload_to_ftp(destination_id, files_to_upload)

        if success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": message,
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": message,
                        "error_type": "UploadError",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Erreur export FTP: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de l'upload FTP",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@export_bp.post("/jobs/<job_id>/sftp")
@jwt_required()
@operator_or_admin_required
def export_job_sftp(job_id: str):
    """
    Upload manuel SFTP pour un job.

    POST /api/export/jobs/<job_id>/sftp
    Body: {"destination_id": 1}

    Returns:
        Résultat upload
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        destination_id = data.get("destination_id")
        if not destination_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "destination_id requis",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Vérifier job existe et appartient à l'utilisateur (avec eager loading)
        from sqlalchemy.orm import joinedload

        job = (
            Job.query.options(joinedload(Job.artifacts))
            .filter_by(job_id=job_id)
            .first()
        )

        if not job:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Job introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        claims = get_jwt()
        user_role = claims.get("role")
        if user_role != "admin" and job.user_id != current_user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        # Vérifier destination existe
        destination = Destination.query.get(destination_id)
        if not destination:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        if destination.type != "sftp":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination n'est pas de type SFTP",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Collecter fichiers à uploader (artifacts déjà chargés)
        release_dir = current_app.config["RELEASES_FOLDER"] / job.release_name
        files_to_upload = []

        for artifact in job.artifacts:
            file_path = release_dir / artifact.file_path
            if file_path.exists():
                files_to_upload.append(file_path)

        if not files_to_upload:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Aucun fichier à uploader",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Upload
        upload_service = FtpUploadService(job_id=job.id)
        success, message = upload_service.upload_to_sftp(
            destination_id, files_to_upload
        )

        if success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": message,
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": message,
                        "error_type": "UploadError",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Erreur export SFTP: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de l'upload SFTP",
                    "error_type": "ServerError",
                }
            ),
            500,
        )
