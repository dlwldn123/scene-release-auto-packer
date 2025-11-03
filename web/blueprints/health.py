"""Health check blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check() -> tuple[dict[str, str], int]:
    """Health check endpoint.

    Returns:
        JSON response with status.
    """
    return jsonify({"status": "ok", "message": "Service is healthy"}), 200
