"""Wizard blueprint for creating releases via 9-step wizard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Configuration, Group, Job, Release, Rule, User

wizard_bp = Blueprint("wizard", __name__)

# Upload directory for wizard files
UPLOAD_DIR = Path("uploads/wizard")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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

    user = db.session.get(User, current_user_id)

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
    rule = db.session.get(Rule, data["rule_id"])
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


@wizard_bp.route("/wizard/<int:release_id>/upload", methods=["POST"])
@jwt_required()
def upload_file(release_id: int) -> tuple[dict, int]:
    """Upload file for wizard step 4.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with file info.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Verify release exists and belongs to user
    release = db.session.get(Release, release_id)
    if not release:
        return {"message": "Release not found"}, 404

    if release.user_id != user.id:
        return {"message": "Permission denied"}, 403

    # Check if file is in request
    if "file" not in request.files:
        # Check for remote URL
        data = request.get_json()
        if data and data.get("file_url"):
            file_url = data["file_url"]
            # Store URL in release metadata
            if not release.release_metadata:
                release.release_metadata = {}
            release.release_metadata["file_url"] = file_url
            release.release_metadata["wizard_step"] = 4
            release.file_path = file_url
            db.session.commit()

            return (
                {
                    "message": "File URL saved successfully",
                    "file_path": file_url,
                    "file_type": "remote",
                },
                200,
            )
        return {"message": "No file or URL provided"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"message": "No file selected"}, 400

    # Validate file size (max 20GB)
    max_size = 20 * 1024 * 1024 * 1024  # 20GB
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > max_size:
        return {"message": "File too large (max 20GB)"}, 400

    # Save file
    filename = f"release_{release_id}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    file.save(str(file_path))

    # Update release
    if not release.release_metadata:
        release.release_metadata = {}
    release.release_metadata["wizard_step"] = 4
    release.release_metadata["file_size"] = file_size
    release.file_path = str(file_path)

    db.session.commit()

    return (
        {
            "message": "File uploaded successfully",
            "file_path": str(file_path),
            "file_type": "local",
            "file_size": file_size,
        },
        200,
    )


@wizard_bp.route("/wizard/<int:release_id>/analyze", methods=["POST"])
@jwt_required()
def analyze_file(release_id: int) -> tuple[dict, int]:
    """Analyze file for wizard step 5.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with analysis results.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Verify release exists and belongs to user
    release = db.session.get(Release, release_id)
    if not release:
        return {"message": "Release not found"}, 404

    if release.user_id != user.id:
        return {"message": "Permission denied"}, 403

    if not release.file_path:
        return {"message": "No file uploaded"}, 400

    # Basic analysis (can be enhanced with MediaInfo for specific formats)
    analysis: dict[str, Any] = {
        "file_path": release.file_path,
        "file_size": release.release_metadata.get("file_size", 0) if release.release_metadata else 0,
    }

    # Extract metadata from filename if possible
    filename = Path(release.file_path).name
    analysis["filename"] = filename

    # Try to extract basic info from filename
    # Format: GroupName-Author-Title-Format-Language-Year-ISBN-eBook
    parts = filename.replace(".epub", "").replace(".pdf", "").replace(".cbz", "").split("-")
    if len(parts) >= 3:
        analysis["detected_group"] = parts[0] if parts else None
        analysis["detected_author"] = parts[1] if len(parts) > 1 else None

    # Update release metadata
    if not release.release_metadata:
        release.release_metadata = {}
    release.release_metadata["wizard_step"] = 5
    release.release_metadata["analysis"] = analysis

    db.session.commit()

    return (
        {
            "message": "File analyzed successfully",
            "analysis": analysis,
        },
        200,
    )


@wizard_bp.route("/wizard/<int:release_id>/metadata", methods=["POST"])
@jwt_required()
def update_metadata(release_id: int) -> tuple[dict, int]:
    """Update metadata for wizard step 6.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with updated metadata.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Verify release exists and belongs to user
    release = db.session.get(Release, release_id)
    if not release:
        return {"message": "Release not found"}, 404

    if release.user_id != user.id:
        return {"message": "Permission denied"}, 403

    data = request.get_json()
    if not data:
        return {"message": "No data provided"}, 400

    # Update release metadata
    if not release.release_metadata:
        release.release_metadata = {}

    # Merge enriched metadata
    enriched_metadata = data.get("enriched_metadata", {})
    release.release_metadata.update(enriched_metadata)
    release.release_metadata["wizard_step"] = 6

    db.session.commit()

    return (
        {
            "message": "Metadata updated successfully",
            "metadata": release.release_metadata,
        },
        200,
    )


@wizard_bp.route("/wizard/<int:release_id>/templates", methods=["GET", "POST"])
@jwt_required()
def handle_templates(release_id: int) -> tuple[dict, int]:
    """Handle templates for wizard step 7.

    GET: List available templates
    POST: Select template for release

    Args:
        release_id: Release ID.

    Returns:
        JSON response with templates or confirmation.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Verify release exists and belongs to user
    release = db.session.get(Release, release_id)
    if not release:
        return {"message": "Release not found"}, 404

    if release.user_id != user.id:
        return {"message": "Permission denied"}, 403

    if request.method == "GET":
        # List available templates (for now, return default)
        templates = [
            {
                "id": 1,
                "name": "Default Template",
                "description": "Default Scene NFO template",
            }
        ]
        return (
            {
                "templates": templates,
            },
            200,
        )

    # POST: Select template
    data = request.get_json()
    template_id = data.get("template_id") if data else None

    # Update release metadata
    if not release.release_metadata:
        release.release_metadata = {}
    release.release_metadata["wizard_step"] = 7
    release.release_metadata["template_id"] = template_id

    db.session.commit()

    return (
        {
            "message": "Template selected successfully",
            "template_id": template_id,
        },
        200,
    )


@wizard_bp.route("/wizard/<int:release_id>/options", methods=["POST"])
@jwt_required()
def update_options(release_id: int) -> tuple[dict, int]:
    """Update packaging options for wizard step 8.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with updated options.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Verify release exists and belongs to user
    release = db.session.get(Release, release_id)
    if not release:
        return {"message": "Release not found"}, 404

    if release.user_id != user.id:
        return {"message": "Permission denied"}, 403

    data = request.get_json()
    if not data:
        return {"message": "No data provided"}, 400

    # Update release config
    options = data.get("options", {})
    if not release.config:
        release.config = {}
    release.config.update(options)

    # Update release metadata
    if not release.release_metadata:
        release.release_metadata = {}
    release.release_metadata["wizard_step"] = 8

    db.session.commit()

    return (
        {
            "message": "Options updated successfully",
            "options": release.config,
        },
        200,
    )


@wizard_bp.route("/wizard/<int:release_id>/finalize", methods=["POST"])
@jwt_required()
def finalize_release(release_id: int) -> tuple[dict, int]:
    """Finalize release for wizard step 9.

    Args:
        release_id: Release ID.

    Returns:
        JSON response with finalized release info.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Verify release exists and belongs to user
    release = db.session.get(Release, release_id)
    if not release:
        return {"message": "Release not found"}, 404

    if release.user_id != user.id:
        return {"message": "Permission denied"}, 403

    data = request.get_json()
    destination_id = data.get("destination_id") if data else None

    # Get job associated with release
    job = Job.query.filter_by(release_id=release_id).first()

    # Update release status
    release.status = "ready"
    if not release.release_metadata:
        release.release_metadata = {}
    release.release_metadata["wizard_step"] = 9
    release.release_metadata["completed"] = True

    if destination_id:
        release.release_metadata["destination_id"] = destination_id

    # Update job status
    if job:
        job.status = "ready"
        if job.config_json:
            job.config_json["destination_id"] = destination_id

    db.session.commit()

    return (
        {
            "message": "Release finalized successfully",
            "release_id": release.id,
            "job_id": job.id if job else None,
            "status": release.status,
        },
        200,
    )
