"""Wizard blueprint for creating releases via 9-step wizard."""

from __future__ import annotations

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Group, Job, Release, Rule, User

wizard_bp = Blueprint("wizard", __name__)


@wizard_bp.route("/wizard/draft", methods=["POST"])
@jwt_required()
def create_draft() -> tuple[dict, int]:
    """Create draft release via wizard (steps 1-3).

    Request body:
        - group: Group name (Scene group)
        - release_type: Release type (EBOOK, TV, DOCS, etc.)
        - rule_id: Selected rule ID

    Returns:
        JSON response with release_id and job_id.
    """
    current_user_id = get_jwt_identity()

    if not current_user_id:
        return {"message": "User not found"}, 404

    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    data = request.get_json()

    # Validate required fields
    if not data.get("group"):
        return {"message": "Group is required"}, 400
    if not data.get("release_type"):
        return {"message": "Release type is required"}, 400
    if not data.get("rule_id"):
        return {"message": "Rule ID is required"}, 400

    # Get or create group
    group_name = data["group"].strip()
    if not group_name:
        return {"message": "Group name cannot be empty"}, 400

    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(name=group_name)
        db.session.add(group)
        db.session.flush()

    # Verify rule exists
    rule = Rule.query.get(data["rule_id"])
    if not rule:
        return {"message": "Rule not found"}, 404

    # Create draft release
    release = Release(
        user_id=user.id,
        group_id=group.id,
        release_type=data["release_type"],
        status="draft",
        release_metadata={"wizard_step": 3},  # Completed steps 1-3
    )
    db.session.add(release)
    db.session.flush()

    # Create job for tracking
    job = Job(
        release_id=release.id,
        created_by=user.id,
        status="draft",
        config_json={
            "group": group_name,
            "release_type": data["release_type"],
            "rule_id": data["rule_id"],
        },
    )
    db.session.add(job)
    db.session.commit()

    return (
        {
            "release_id": release.id,
            "job_id": job.id,
            "message": "Draft release created successfully",
        },
        201,
    )


@wizard_bp.route("/wizard/rules", methods=["GET"])
@jwt_required()
def list_rules() -> tuple[dict, int]:
    """List rules filtered by release type.

    Query parameters:
        - release_type: Filter by release type (EBOOK, TV, etc.)

    Returns:
        JSON response with rules list.
    """
    release_type = request.args.get("release_type", "").upper()

    query = Rule.query

    if release_type:
        # Filter by section matching release type
        if release_type == "EBOOK":
            query = query.filter(Rule.section == "eBOOK")
        elif release_type == "TV":
            query = query.filter(Rule.section.in_(["TV-720p", "TV-SD"]))
        # Add more filters as needed

    rules = query.all()

    return (
        {
            "rules": [rule.to_dict() for rule in rules],
        },
        200,
    )
