"""Releases blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Release, User

releases_bp = Blueprint("releases", __name__)


@releases_bp.route("/releases", methods=["GET"])
@jwt_required()
def list_releases() -> tuple[dict, int]:
    """List releases with filters and pagination.

    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - release_type: Filter by release type
        - status: Filter by status
        - user_id: Filter by user ID

    Returns:
        JSON response with releases list and pagination info.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    release_type = request.args.get("release_type", "").upper()
    status = request.args.get("status", "")
    user_id = request.args.get("user_id", type=int)

    # Build query
    query = Release.query

    if release_type:
        query = query.filter(Release.release_type == release_type)

    if status:
        query = query.filter(Release.status == status)

    if user_id:
        query = query.filter(Release.user_id == user_id)

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    releases = pagination.items

    return (
        {
            "releases": [release.to_dict() for release in releases],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        },
        200,
    )


@releases_bp.route("/releases/<int:release_id>", methods=["GET"])
@jwt_required()
def get_release(release_id: int) -> tuple[dict, int]:
    """Get release by ID.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with release data.
    """
    current_user_id = get_jwt_identity()
    release = Release.query.get(release_id)

    if not release:
        return {"message": "Release not found"}, 404

    # Check permissions (user can only view their own releases unless admin)
    if release.user_id != current_user_id:
        # TODO: Check admin permissions
        return {"message": "Permission denied"}, 403

    return {"release": release.to_dict()}, 200


@releases_bp.route("/releases/<int:release_id>", methods=["DELETE"])
@jwt_required()
def delete_release(release_id: int) -> tuple[dict, int]:
    """Delete release.

    Args:
        release_id: Release ID.

    Returns:
        JSON response.
    """
    current_user_id = get_jwt_identity()
    release = Release.query.get(release_id)

    if not release:
        return {"message": "Release not found"}, 404

    # Check permissions
    if release.user_id != current_user_id:
        return {"message": "Permission denied"}, 403

    db.session.delete(release)
    db.session.commit()

    return {"message": "Release deleted successfully"}, 200
