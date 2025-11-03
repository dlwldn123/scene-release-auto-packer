"""Releases actions blueprint for special actions (NFOFIX, READNFO, REPACK, DIRFIX)."""

from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Job, Release, User

releases_actions_bp = Blueprint("releases_actions", __name__)


def _check_permission(release: Release, current_user_id: int, action: str) -> bool:
    """Check if user has permission for action.

    Args:
        release: Release object.
        current_user_id: Current user ID.
        action: Action name (nfofix, readnfo, repack, dirfix).

    Returns:
        True if user has permission, False otherwise.
    """
    # User can perform actions on their own releases
    if release.user_id == current_user_id:
        return True

    # TODO: Check MOD permission for other users' releases
    # For now, only allow on own releases
    return False


@releases_actions_bp.route(
    "/releases/<int:release_id>/actions/nfofix", methods=["POST"]
)
@jwt_required()
def nfofix_release(release_id: int) -> tuple[dict, int]:
    """Fix NFO file for a release.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with job ID.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    release = Release.query.get(release_id)

    if not release:
        return {"message": "Release not found"}, 404

    if not _check_permission(release, current_user_id, "nfofix"):
        return {"message": "Permission denied"}, 403

    # Create job for NFOFIX action
    job = Job(
        release_id=release.id,
        created_by=current_user_id,
        status="pending",
        job_type="nfofix",
        config_json={"action": "nfofix"},
    )
    db.session.add(job)
    db.session.commit()

    return (
        {
            "message": "NFOFIX job created successfully",
            "job_id": job.id,
        },
        200,
    )


@releases_actions_bp.route(
    "/releases/<int:release_id>/actions/readnfo", methods=["POST"]
)
@jwt_required()
def readnfo_release(release_id: int) -> tuple[dict, int]:
    """Read NFO file and regenerate release structure.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with job ID.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    release = Release.query.get(release_id)

    if not release:
        return {"message": "Release not found"}, 404

    if not _check_permission(release, current_user_id, "readnfo"):
        return {"message": "Permission denied"}, 403

    if not release.file_path:
        return {"message": "Release file path not found"}, 400

    # Create job for READNFO action
    job = Job(
        release_id=release.id,
        created_by=current_user_id,
        status="pending",
        job_type="readnfo",
        config_json={"action": "readnfo", "file_path": release.file_path},
    )
    db.session.add(job)
    db.session.commit()

    return (
        {
            "message": "READNFO job created successfully",
            "job_id": job.id,
        },
        200,
    )


@releases_actions_bp.route(
    "/releases/<int:release_id>/actions/repack", methods=["POST"]
)
@jwt_required()
def repack_release(release_id: int) -> tuple[dict, int]:
    """Repack a release with new options.

    Args:
        release_id: Release ID.

    Request body:
        - zip_size: New ZIP size (optional)
        - template_id: New template ID (optional)

    Returns:
        JSON response with job ID.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    release = Release.query.get(release_id)

    if not release:
        return {"message": "Release not found"}, 404

    if not _check_permission(release, current_user_id, "repack"):
        return {"message": "Permission denied"}, 403

    data = request.get_json() or {}
    config = release.config or {}
    config.update(data)

    # Create job for REPACK action
    job = Job(
        release_id=release.id,
        created_by=current_user_id,
        status="pending",
        job_type="repack",
        config_json={"action": "repack", **config},
    )
    db.session.add(job)
    db.session.commit()

    return (
        {
            "message": "REPACK job created successfully",
            "job_id": job.id,
        },
        200,
    )


@releases_actions_bp.route(
    "/releases/<int:release_id>/actions/dirfix", methods=["POST"]
)
@jwt_required()
def dirfix_release(release_id: int) -> tuple[dict, int]:
    """Fix directory structure for a release.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with job ID.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    release = Release.query.get(release_id)

    if not release:
        return {"message": "Release not found"}, 404

    if not _check_permission(release, current_user_id, "dirfix"):
        return {"message": "Permission denied"}, 403

    if not release.file_path:
        return {"message": "Release file path not found"}, 400

    # Create job for DIRFIX action
    job = Job(
        release_id=release.id,
        created_by=current_user_id,
        status="pending",
        job_type="dirfix",
        config_json={"action": "dirfix", "file_path": release.file_path},
    )
    db.session.add(job)
    db.session.commit()

    return (
        {
            "message": "DIRFIX job created successfully",
            "job_id": job.id,
        },
        200,
    )
