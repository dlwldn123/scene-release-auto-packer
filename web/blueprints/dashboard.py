"""Dashboard blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from web.extensions import cache, db
from web.models import Job, Release, User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/stats", methods=["GET"])
@jwt_required()
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_stats() -> tuple[dict, int]:
    """Get dashboard statistics.

    Returns:
        JSON response with statistics.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Optimized queries with db.func.count to avoid N+1 queries
    total_releases = db.session.query(func.count(Release.id)).scalar() or 0
    total_jobs = db.session.query(func.count(Job.id)).scalar() or 0
    user_releases = (
        db.session.query(func.count(Release.id))
        .filter(Release.user_id == current_user_id)
        .scalar()
        or 0
    )
    user_jobs = (
        db.session.query(func.count(Job.id))
        .filter(Job.created_by == current_user_id)
        .scalar()
        or 0
    )

    return (
        {
            "total_releases": total_releases,
            "total_jobs": total_jobs,
            "user_releases": user_releases,
            "user_jobs": user_jobs,
            "user": user.to_dict(),
        },
        200,
    )
