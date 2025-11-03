"""Wizard blueprint for new release creation."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Job, Release, User
from web.utils.validators import validate_release_type, validate_scene_group

wizard_bp = Blueprint("wizard", __name__)


@wizard_bp.route("/wizard/draft", methods=["POST", "PUT"])
@jwt_required()
def save_draft() -> tuple[dict, int]:
    """Save or update wizard draft.

    Returns:
        JSON response with draft job ID.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    data = request.get_json()
    if not data:
        return {"message": "No input data provided"}, 400

    # Validate step data
    step = data.get("step")
    step_data = data.get("step_data", {})

    if step == 1:
        # Step 1: Group
        group = step_data.get("group", "").strip()
        if not validate_scene_group(group):
            return {"message": "Invalid Scene group format"}, 400

    elif step == 2:
        # Step 2: Release Type
        release_type = step_data.get("release_type", "").upper()
        if not validate_release_type(release_type):
            return {"message": "Invalid release type"}, 400

    # Get or create draft job
    job_id = data.get("job_id")
    if job_id:
        job = Job.query.get(job_id)
        if not job or job.created_by != current_user_id:
            return {"message": "Job not found"}, 404
    else:
        job = Job(
            status="draft",
            config_json={"steps": {}},
            created_by=current_user_id,
        )
        db.session.add(job)
        db.session.flush()

    # Update job config with step data
    if not job.config_json:
        job.config_json = {"steps": {}}

    job.config_json["steps"][str(step)] = step_data
    job.config_json["current_step"] = step

    db.session.commit()

    return {"job_id": job.id, "step": step}, 200


@wizard_bp.route("/wizard/draft/<int:job_id>", methods=["GET"])
@jwt_required()
def get_draft(job_id: int) -> tuple[dict, int]:
    """Get wizard draft.

    Args:
        job_id: Job ID.

    Returns:
        JSON response with draft data.
    """
    current_user_id = get_jwt_identity()
    job = Job.query.get(job_id)

    if not job or job.created_by != current_user_id:
        return {"message": "Job not found"}, 404

    return {"job_id": job.id, "config": job.config_json}, 200


@wizard_bp.route("/wizard/rules", methods=["GET"])
@jwt_required()
def list_rules() -> tuple[dict, int]:
    """List available rules.

    Returns:
        JSON response with rules list.
    """
    from web.models import Rule

    release_type = request.args.get("release_type", "").upper()
    scene = request.args.get("scene", "")
    section = request.args.get("section", "")

    query = Rule.query

    if release_type:
        # Filter by release type (rules contain release type info)
        query = query.filter(Rule.name.contains(release_type))

    if scene:
        query = query.filter(Rule.scene == scene)

    if section:
        query = query.filter(Rule.section == section)

    rules = query.all()

    return (
        {
            "rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "scene": rule.scene,
                    "section": rule.section,
                    "year": rule.year,
                }
                for rule in rules
            ]
        },
        200,
    )
