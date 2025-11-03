"""
Blueprint pour la gestion des jobs de packaging.
"""

import logging
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from web.auth import operator_or_admin_required
from web.database import db
from web.helpers import get_current_user_id
from web.models.destination import Destination
from web.models.job import Artifact, Job, JobLog, JobStatus
from web.models.user import User
from web.schemas.job import JobResponseSchema

logger = logging.getLogger(__name__)

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("")
@jwt_required()
@operator_or_admin_required
def list_jobs():
    """
    Liste les jobs avec filtres.

    GET /api/jobs?status=completed&type=EBOOK&limit=10

    Returns:
        Liste des jobs avec pagination
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Filtres
        status = request.args.get("status")
        job_type = request.args.get("type")
        user_id = request.args.get("user_id")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        # Query de base
        query = Job.query

        # Admin peut voir tous les jobs, operator seulement les siens
        if user_role != "admin":
            query = query.filter_by(user_id=current_user_id)
        elif user_id:
            query = query.filter_by(user_id=int(user_id))

        # Filtres
        if status:
            try:
                status_enum = JobStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                pass

        if job_type:
            query = query.filter_by(type=job_type)

        # Ordre et pagination avec optimisations N+1
        query = query.order_by(Job.created_at.desc())
        # Optimisation : précharger logs et artifacts pour éviter N+1
        query = query.options(joinedload(Job.logs), joinedload(Job.artifacts))
        total = query.count()
        jobs = query.limit(limit).offset(offset).all()

        # Serialization
        schema = JobResponseSchema(many=True)
        jobs_data = schema.dump(jobs)

        return (
            jsonify(
                {
                    "success": True,
                    "jobs": jobs_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste jobs: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des jobs",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@jobs_bp.get("/<job_id>")
@jwt_required()
@operator_or_admin_required
def get_job(job_id: str):
    """
    Récupère les détails d'un job.

    GET /api/jobs/<job_id>

    Returns:
        Détails du job avec logs et artefacts
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Rechercher job avec eager loading pour éviter N+1
        from sqlalchemy.orm import joinedload

        job = (
            Job.query.options(joinedload(Job.logs), joinedload(Job.artifacts))
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

        # Vérifier permissions
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

        # Serialization
        schema = JobResponseSchema()
        job_data = schema.dump(job)

        # Ajouter logs et artefacts (déjà chargés via eager loading)
        job_data["logs"] = [
            {
                "level": log.level,
                "message": log.message,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in sorted(job.logs, key=lambda x: x.timestamp)
        ]

        job_data["artifacts"] = [
            {
                "id": artifact.id,
                "file_path": artifact.file_path,
                "file_type": artifact.file_type,
                "file_size": artifact.file_size,
                "crc32": artifact.crc32,
                "created_at": artifact.created_at.isoformat(),
            }
            for artifact in job.artifacts
        ]

        return (
            jsonify(
                {
                    "success": True,
                    "job": job_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération job: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération du job",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@jobs_bp.get("/<job_id>/logs")
@jwt_required()
@operator_or_admin_required
def get_job_logs(job_id: str):
    """
    Récupère les logs d'un job.

    GET /api/jobs/<job_id>/logs

    Returns:
        Liste des logs du job
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Rechercher job
        job = Job.query.filter_by(job_id=job_id).first()

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

        # Vérifier permissions
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

        # Récupérer logs
        logs = job.logs.order_by(JobLog.timestamp).all()

        logs_data = [
            {
                "level": log.level,
                "message": log.message,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ]

        return (
            jsonify(
                {
                    "success": True,
                    "logs": logs_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération logs: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des logs",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@jobs_bp.get("/<job_id>/artifacts")
@jwt_required()
@operator_or_admin_required
def get_job_artifacts(job_id: str):
    """
    Récupère les artefacts d'un job.

    GET /api/jobs/<job_id>/artifacts

    Returns:
        Liste des artefacts du job
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Rechercher job avec eager loading pour éviter N+1
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

        # Vérifier permissions
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

        # Artifacts déjà chargés via eager loading
        artifacts = job.artifacts

        artifacts_data = [
            {
                "id": artifact.id,
                "file_path": artifact.file_path,
                "file_type": artifact.file_type,
                "file_size": artifact.file_size,
                "crc32": artifact.crc32,
                "created_at": artifact.created_at.isoformat(),
            }
            for artifact in artifacts
        ]

        return (
            jsonify(
                {
                    "success": True,
                    "artifacts": artifacts_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération artefacts: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des artefacts",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@jobs_bp.delete("/<job_id>")
@jwt_required()
@operator_or_admin_required
def delete_job(job_id: str):
    """
    Supprime un job et ses artefacts.

    DELETE /api/jobs/<job_id>

    Returns:
        Confirmation suppression
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Rechercher job
        job = Job.query.filter_by(job_id=job_id).first()

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

        # Vérifier permissions
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

        # Supprimer job (cascade supprimera logs et artefacts)
        db.session.delete(job)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Job supprimé avec succès",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur suppression job: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la suppression du job",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@jobs_bp.post("/<job_id>/export/ftp")
@jwt_required()
@operator_or_admin_required
def export_job_ftp(job_id: str):
    """
    Upload manuel des artefacts d'un job vers destination FTP.

    POST /api/jobs/<job_id>/export/ftp
    Body: {"destination_id": 1} ou {"destination_name": "..."}

    Returns:
        Résultat de l'upload
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Rechercher job
        job = Job.query.filter_by(job_id=job_id).first()

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

        # Vérifier permissions
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

        # Vérifier que le job est complété
        if job.status != JobStatus.COMPLETED:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Le job doit être complété pour être uploadé",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Récupérer destination
        data = request.get_json() or {}
        destination_id = data.get("destination_id")
        destination_name = data.get("destination_name")

        if destination_id:
            destination = Destination.query.get(destination_id)
        elif destination_name:
            destination = Destination.query.filter_by(
                name=destination_name,
                user_id=current_user_id,
            ).first()
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "destination_id ou destination_name requis",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

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
                        "error": "La destination doit être de type FTP",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Collecter fichiers à uploader
        from web.services.packaging import PackagingService

        packaging_service = PackagingService(user_id=current_user_id)

        # Déterminer release_dir depuis job config
        output_dir = job.config.get("output_dir")
        release_name = job.release_name or job.config.get("release_name", "")

        if output_dir:
            release_dir = Path(output_dir) / release_name
        else:
            release_dir = Path("releases") / release_name

        if not release_dir.exists():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Dossier release introuvable: {release_dir}",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

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
        from web.services.ftp_upload import FtpUploadService

        upload_service = FtpUploadService()

        success, message = upload_service.upload_to_ftp(
            destination_id=destination.id,
            files=files_to_upload,
            destination=destination,
            job_id=job.job_id,
        )

        if success:
            job.add_log("INFO", f"Upload FTP manuel réussi: {message}")
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
            job.add_log("ERROR", f"Upload FTP manuel échoué: {message}")
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


@jobs_bp.post("/<job_id>/export/sftp")
@jwt_required()
@operator_or_admin_required
def export_job_sftp(job_id: str):
    """
    Upload manuel des artefacts d'un job vers destination SFTP.

    POST /api/jobs/<job_id>/export/sftp
    Body: {"destination_id": 1} ou {"destination_name": "..."}

    Returns:
        Résultat de l'upload
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Rechercher job
        job = Job.query.filter_by(job_id=job_id).first()

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

        # Vérifier permissions
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

        # Vérifier que le job est complété
        if job.status != JobStatus.COMPLETED:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Le job doit être complété pour être uploadé",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Récupérer destination
        data = request.get_json() or {}
        destination_id = data.get("destination_id")
        destination_name = data.get("destination_name")

        if destination_id:
            destination = Destination.query.get(destination_id)
        elif destination_name:
            destination = Destination.query.filter_by(
                name=destination_name,
                user_id=current_user_id,
            ).first()
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "destination_id ou destination_name requis",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

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
                        "error": "La destination doit être de type SFTP",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Collecter fichiers à uploader
        output_dir = job.config.get("output_dir")
        release_name = job.release_name or job.config.get("release_name", "")

        if output_dir:
            release_dir = Path(output_dir) / release_name
        else:
            release_dir = Path("releases") / release_name

        if not release_dir.exists():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Dossier release introuvable: {release_dir}",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

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
        from web.services.ftp_upload import FtpUploadService

        upload_service = FtpUploadService()

        success, message = upload_service.upload_to_sftp(
            destination_id=destination.id,
            files=files_to_upload,
            destination=destination,
            job_id=job.job_id,
        )

        if success:
            job.add_log("INFO", f"Upload SFTP manuel réussi: {message}")
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
            job.add_log("ERROR", f"Upload SFTP manuel échoué: {message}")
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
