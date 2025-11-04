"""Releases blueprint."""

from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import String, cast
from sqlalchemy.orm import Query, joinedload, selectinload

from web.extensions import db
from web.models import Release, User
from web.utils.permissions import check_permission

releases_bp = Blueprint("releases", __name__)


def _apply_sorting(query: Query, sort_by: str, sort_order: str) -> Query:
    """Apply sorting to query.

    Args:
        query: SQLAlchemy query object.
        sort_by: Field to sort by (created_at, release_type, status).
        sort_order: Sort order (asc, desc).

    Returns:
        Query with sorting applied.
    """
    sort_fields = {
        "created_at": Release.created_at,
        "release_type": Release.release_type,
        "status": Release.status,
    }

    field = sort_fields.get(sort_by, Release.created_at)
    if sort_order == "desc":
        return query.order_by(field.desc())
    return query.order_by(field.asc())


@releases_bp.route("/releases", methods=["GET"])
@jwt_required()
def list_releases() -> tuple[dict, int]:
    """List releases with filters, search, sorting and pagination.

    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - release_type: Filter by release type
        - status: Filter by status
        - user_id: Filter by user ID
        - group_id: Filter by group ID
        - search: Text search in metadata
        - sort_by: Sort field (created_at, release_type)
        - sort_order: Sort order (asc, desc)

    Returns:
        JSON response with releases list and pagination info.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    release_type = request.args.get("release_type", "").upper()
    status = request.args.get("status", "")
    user_id = request.args.get("user_id", type=int)
    search = request.args.get("search", "").strip()
    group_id = request.args.get("group_id", type=int)
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")

    # Build query with eager loading to avoid N+1 queries
    query = Release.query.options(
        joinedload(Release.user),
        joinedload(Release.group),
        selectinload(Release.jobs),
    )

    # Filter by release type
    if release_type:
        query = query.filter(Release.release_type == release_type)

    # Filter by status
    if status:
        query = query.filter(Release.status == status)

    # Filter by user ID
    if user_id:
        query = query.filter(Release.user_id == user_id)

    # Filter by group ID
    if group_id:
        query = query.filter(Release.group_id == group_id)

    # Text search (in metadata JSON)
    if search:
        # MySQL JSON search: convert JSON to text and use LIKE
        search_pattern = f"%{search}%"
        query = query.filter(
            cast(Release.release_metadata, String).like(search_pattern)
        )

    # Sorting
    query = _apply_sorting(query, sort_by, sort_order)

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
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    release = db.session.get(Release, release_id)

    if not release:
        return {"message": "Release not found"}, 404

    # Check permissions (user can only view their own releases unless has READ permission)
    if release.user_id != current_user_id:
        if not check_permission(user, "releases", "read", release.user_id):
            return {"message": "Permission denied"}, 403

    return {"release": release.to_dict()}, 200


@releases_bp.route("/releases/<int:release_id>", methods=["PUT"])
@jwt_required()
def update_release(release_id: int) -> tuple[dict, int]:
    """Update release.

    Args:
        release_id: Release ID.

    Request body:
        - release_metadata: Updated metadata (optional)
        - config: Updated config (optional)
        - status: Updated status (optional)

    Returns:
        JSON response with updated release data.
    """
    current_user_id = get_jwt_identity()
    release = db.session.get(Release, release_id)

    if not release:
        return {"message": "Release not found"}, 404

    # Check permissions (user can update their own releases or if has MOD permission)
    user = db.session.get(User, current_user_id)
    if not user:
        return {"message": "User not found"}, 404

    if release.user_id != current_user_id:
        if not check_permission(user, "releases", "mod", release.user_id):
            return {"message": "Permission denied"}, 403

    data = request.get_json()

    # Update fields if provided
    if "release_metadata" in data:
        release.release_metadata = data["release_metadata"]
    if "config" in data:
        release.config = data["config"]
    if "status" in data:
        release.status = data["status"]

    db.session.commit()

    return {
        "release": release.to_dict(),
        "message": "Release updated successfully",
    }, 200


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
    release = db.session.get(Release, release_id)

    if not release:
        return {"message": "Release not found"}, 404

    # Check permissions (user can delete their own releases or if has DELETE permission)
    user = db.session.get(User, current_user_id)
    if not user:
        return {"message": "User not found"}, 404

    if release.user_id != current_user_id:
        if not check_permission(user, "releases", "delete", release.user_id):
            return {"message": "Permission denied"}, 403

    db.session.delete(release)
    db.session.commit()

    return {"message": "Release deleted successfully"}, 200
