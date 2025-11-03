# Health check endpoint pour Docker
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health_check():
    """
    Endpoint de health check pour Docker/Kubernetes.

    Returns:
        Status 200 avec informations de santé
    """
    try:
        from web.database import db

        # Test connexion DB
        db.session.execute(db.text("SELECT 1"))

        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "packer-backend",
                    "database": "connected",
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "service": "packer-backend",
                    "database": "disconnected",
                    "error": str(e),
                }
            ),
            503,
        )
