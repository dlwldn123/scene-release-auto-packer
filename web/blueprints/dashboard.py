"""Dashboard blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Job, Release, User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/stats", methods=["GET"])
@jwt_required()
def get_stats() -> tuple[dict, int]:
    """Get dashboard statistics.

    Returns:
        JSON response with statistics.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Get statistics
    total_releases = Release.query.count()
    total_jobs = Job.query.count()
    user_releases = Release.query.filter_by(user_id=current_user_id).count()
    user_jobs = Job.query.filter_by(created_by=current_user_id).count()

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
