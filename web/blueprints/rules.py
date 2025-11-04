"""Rules blueprint."""

from __future__ import annotations

import re

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from web.extensions import db
from web.models import Rule, User
from web.services.scenerules_download import ScenerulesDownloadService
from web.utils.permissions import check_permission

rules_bp = Blueprint("rules", __name__)


@rules_bp.route("/rules", methods=["GET"])
@jwt_required()
@cache.cached(timeout=600, query_string=True)  # Cache for 10 minutes
def list_rules() -> tuple[dict, int]:
    """List rules with filters and pagination.

    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - scene: Filter by scene name
        - section: Filter by section
        - year: Filter by year

    Returns:
        JSON response with rules list and pagination info.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    scene = request.args.get("scene", "")
    section = request.args.get("section", "")
    year = request.args.get("year", type=int)
    search = request.args.get("search", "")

    # Build query
    query = Rule.query

    if scene:
        query = query.filter(Rule.scene == scene)

    if section:
        query = query.filter(Rule.section == section)

    if year:
        query = query.filter(Rule.year == year)

    # Text search in name and content
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Rule.name.like(search_pattern)) | (Rule.content.like(search_pattern))
        )

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rules = pagination.items

    return (
        {
            "rules": [rule.to_dict() for rule in rules],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        },
        200,
    )


@rules_bp.route("/rules/<int:rule_id>", methods=["GET"])
@jwt_required()
def get_rule(rule_id: int) -> tuple[dict, int]:
    """Get rule by ID.

    Args:
        rule_id: Rule ID.

    Returns:
        JSON response with rule data.
    """
    rule = db.session.get(Rule, rule_id)

    if not rule:
        return {"message": "Rule not found"}, 404

    return {"rule": rule.to_dict()}, 200


@rules_bp.route("/rules", methods=["POST"])
@jwt_required()
def create_rule() -> tuple[dict, int]:
    """Create a new rule.

    Expected JSON:
        - name: Rule name
        - content: Rule content
        - scene: Scene name (optional)
        - section: Section (optional)
        - year: Year (optional)

    Returns:
        JSON response with created rule.
    """
    # User already verified by @jwt_required()
    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    required_fields = ["name", "content"]
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400

    rule = Rule(
        name=data["name"],
        content=data["content"],
        scene=data.get("scene"),
        section=data.get("section"),
        year=data.get("year"),
    )

    db.session.add(rule)
    db.session.commit()

    return {"rule": rule.to_dict()}, 201


@rules_bp.route("/rules/<int:rule_id>", methods=["PUT"])
@jwt_required()
def update_rule(rule_id: int) -> tuple[dict, int]:
    """Update rule.

    Args:
        rule_id: Rule ID.

    Expected JSON:
        - name: Rule name (optional)
        - content: Rule content (optional)
        - scene: Scene name (optional)
        - section: Section (optional)
        - year: Year (optional)

    Returns:
        JSON response with updated rule.
    """
    rule = db.session.get(Rule, rule_id)

    if not rule:
        return {"message": "Rule not found"}, 404

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    # Update fields if provided
    if "name" in data:
        rule.name = data["name"]
    if "content" in data:
        rule.content = data["content"]
    if "scene" in data:
        rule.scene = data["scene"]
    if "section" in data:
        rule.section = data["section"]
    if "year" in data:
        rule.year = data["year"]

    db.session.commit()

    return {"rule": rule.to_dict()}, 200


@rules_bp.route("/rules/<int:rule_id>", methods=["DELETE"])
@jwt_required()
def delete_rule(rule_id: int) -> tuple[dict, int]:
    """Delete rule.

    Args:
        rule_id: Rule ID.

    Returns:
        JSON response.
    """
    rule = db.session.get(Rule, rule_id)

    if not rule:
        return {"message": "Rule not found"}, 404

    db.session.delete(rule)
    db.session.commit()

    return {"message": "Rule deleted successfully"}, 200


@rules_bp.route("/rules/scenerules", methods=["GET"])
@jwt_required()
def list_scenerules_rules() -> tuple[dict, int]:
    """List available rules on scenerules.org.

    Query parameters:
        - scene: Filter by scene name
        - section: Filter by section
        - year: Filter by year

    Returns:
        JSON response with available rules list.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Get filters
    scene_filter = request.args.get("scene", "")
    section_filter = request.args.get("section", "")
    year_filter = request.args.get("year", type=int)

    # Get available rules from scenerules.org
    downloader = ScenerulesDownloadService()
    available_rules = downloader.list_available_rules()

    # Apply filters
    filtered_rules = available_rules
    if scene_filter:
        filtered_rules = [
            r
            for r in filtered_rules
            if r.get("scene", "").lower() == scene_filter.lower()
        ]
    if section_filter:
        filtered_rules = [
            r
            for r in filtered_rules
            if r.get("section", "").lower() == section_filter.lower()
        ]
    if year_filter:
        filtered_rules = [r for r in filtered_rules if r.get("year") == year_filter]

    # Check which rules are already downloaded locally
    local_rules = Rule.query.all()
    local_rule_keys = {
        (r.section, r.year): r.id for r in local_rules if r.section and r.year
    }

    # Add indicator if rule is already downloaded
    for rule in filtered_rules:
        rule_key = (rule.get("section"), rule.get("year"))
        rule["is_downloaded"] = rule_key in local_rule_keys
        if rule["is_downloaded"]:
            rule["local_rule_id"] = local_rule_keys[rule_key]

    return (
        {
            "rules": filtered_rules,
            "total": len(filtered_rules),
        },
        200,
    )


@rules_bp.route("/rules/scenerules/download", methods=["POST"])
@jwt_required()
def download_scenerules_rule() -> tuple[dict, int]:
    """Download a rule from scenerules.org.

    Expected JSON:
        - section: Rule section (eBOOK, TV-720p, etc.)
        - year: Rule year (optional, default: 2022)
        - scene: Scene name (optional, default: English)
        - url: Direct URL to rule NFO (optional, alternative to section/year)

    Returns:
        JSON response with downloaded rule.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Check WRITE permission
    if not check_permission(user, "rules", "write"):
        return {"message": "Permission denied"}, 403

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    downloader = ScenerulesDownloadService()

    try:
        # Download rule
        if "url" in data:
            rule_data = downloader.download_rule_by_url(data["url"])
        else:
            section = data.get("section")
            if not section:
                return {"message": "Section is required"}, 400

            year = data.get("year", 2022)
            scene = data.get("scene", "English")
            rule_data = downloader.download_rule(section, year, scene)

        # Check if rule already exists locally
        existing_rule = Rule.query.filter_by(
            section=rule_data["section"], year=rule_data["year"]
        ).first()

        if existing_rule:
            # Update existing rule
            existing_rule.name = rule_data["name"]
            existing_rule.content = rule_data["content"]
            existing_rule.scene = rule_data.get("scene")
            db.session.commit()

            return (
                {
                    "rule": existing_rule.to_dict(),
                    "message": "Rule updated successfully",
                    "was_existing": True,
                },
                200,
            )

        # Create new rule
        rule = Rule(
            name=rule_data["name"],
            content=rule_data["content"],
            section=rule_data["section"],
            year=rule_data["year"],
            scene=rule_data.get("scene"),
        )

        db.session.add(rule)
        db.session.commit()

        return (
            {
                "rule": rule.to_dict(),
                "message": "Rule downloaded successfully",
                "was_existing": False,
            },
            201,
        )

    except ValueError as e:
        return {"message": str(e)}, 404
    except Exception as e:
        return {"message": f"Failed to download rule: {str(e)}"}, 500


def _extract_metadata_from_content(content: str) -> dict[str, str | int | None]:
    """Extract metadata (scene, section, year) from rule content.

    Args:
        content: Rule content (NFO format).

    Returns:
        Dictionary with extracted metadata (scene, section, year).
    """
    metadata: dict[str, str | int | None] = {
        "scene": None,
        "section": None,
        "year": None,
    }

    # Extract scene (look for common scene names)
    scene_patterns = [
        r"\[(English|Baltic|Danish|Dutch|Flemish|French|German|Hungarian|Italian|Lithuanian|Polish|Spanish|Swedish)\s*Scene\]",
        r"Scene\s*[:;]\s*(English|Baltic|Danish|Dutch|Flemish|French|German|Hungarian|Italian|Lithuanian|Polish|Spanish|Swedish)",
    ]
    for pattern in scene_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            metadata["scene"] = match.group(1)
            break

    # Extract section (look for section names like eBOOK, TV-720p, etc.)
    section_patterns = [
        r"\[(\d{4})\]\s*(eBOOK|TV-720p|TV-SD|X264|X265|BLURAY|MP3|FLAC)",
        r"Section\s*[:;]\s*(eBOOK|TV-720p|TV-SD|X264|X265|BLURAY|MP3|FLAC)",
        r"^([A-Z0-9-]+)\s+Rules?\s+\[(\d{4})\]",
    ]
    for pattern in section_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                metadata["section"] = match.group(1) or match.group(2)
            else:
                metadata["section"] = match.group(1)
            break

    # Extract year (look for [YYYY] pattern)
    year_patterns = [
        r"\[(\d{4})\]",  # [2022]
        r"\((\d{4})\)",  # (2022)
        r"\b(19\d{2}|20\d{2})\b",  # 4-digit year
    ]
    for pattern in year_patterns:
        matches = re.findall(pattern, content)
        if matches:
            # Take the most recent year found
            years = [int(m) for m in matches if 1900 <= int(m) <= 2100]
            if years:
                metadata["year"] = max(years)
                break

    return metadata


@rules_bp.route("/rules/upload", methods=["POST"])
@jwt_required()
def upload_rule() -> tuple[dict, int]:
    """Upload a rule file.

    Expected form data:
        - file: Rule file (NFO, TXT)
        - name: Rule name (optional, defaults to filename)
        - scene: Scene name (optional, auto-extracted if not provided)
        - section: Section (optional, auto-extracted if not provided)
        - year: Year (optional, auto-extracted if not provided)

    Returns:
        JSON response with created rule and extracted metadata.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Check if file is present
    if "file" not in request.files:
        return {"message": "No file provided"}, 400

    file = request.files["file"]

    if file.filename == "":
        return {"message": "No file selected"}, 400

    # Validate file extension
    allowed_extensions = {".nfo", ".txt", ".txt.nfo"}
    filename = secure_filename(file.filename)
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return {
            "message": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        }, 400

    # Read file content
    try:
        # Try UTF-8 first
        file.seek(0)
        content = file.read().decode("utf-8")
    except UnicodeDecodeError:
        try:
            # Try ISO-8859-1 (common for NFO files)
            file.seek(0)
            content = file.read().decode("iso-8859-1")
        except UnicodeDecodeError:
            return {"message": "Invalid file encoding"}, 400

    # Get metadata from form or extract from content
    name = request.form.get("name") or filename.rsplit(".", 1)[0]
    scene = request.form.get("scene")
    section = request.form.get("section")
    year = request.form.get("year", type=int)

    # Extract metadata from content if not provided
    if not scene or not section or not year:
        extracted = _extract_metadata_from_content(content)
        scene = scene or extracted.get("scene")
        section = section or extracted.get("section")
        year = year or extracted.get("year")

    # Create rule
    rule = Rule(
        name=name,
        content=content,
        scene=scene,
        section=section,
        year=year,
    )

    db.session.add(rule)
    db.session.commit()

    return (
        {
            "rule": rule.to_dict(),
            "message": "Rule uploaded successfully",
            "metadata_extracted": {
                "scene": scene,
                "section": section,
                "year": year,
            },
        },
        201,
    )
