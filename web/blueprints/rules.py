"""Rules blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Rule, User

rules_bp = Blueprint("rules", __name__)


@rules_bp.route("/rules", methods=["GET"])
@jwt_required()
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
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    scene = request.args.get("scene", "")
    section = request.args.get("section", "")
    year = request.args.get("year", type=int)

    # Build query
    query = Rule.query

    if scene:
        query = query.filter(Rule.scene == scene)

    if section:
        query = query.filter(Rule.section == section)

    if year:
        query = query.filter(Rule.year == year)

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
    rule = Rule.query.get(rule_id)

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
    current_user_id = get_jwt_identity()
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
    rule = Rule.query.get(rule_id)

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
    rule = Rule.query.get(rule_id)

    if not rule:
        return {"message": "Rule not found"}, 404

    db.session.delete(rule)
    db.session.commit()

    return {"message": "Rule deleted successfully"}, 200
