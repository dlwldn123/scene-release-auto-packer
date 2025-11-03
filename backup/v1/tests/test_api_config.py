"""
Tests pour le blueprint API Config.
"""

from unittest.mock import Mock, patch

import pytest
from flask import Flask

from web.blueprints.api_config import api_config_bp
from web.database import db
from web.models.api_config import ApiConfig
from web.models.user import User


@pytest.fixture
def app():
    """Fixture application Flask pour tests."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret-key"

    db.init_app(app)
    app.register_blueprint(api_config_bp, url_prefix="/api/config")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture client de test."""
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Créer utilisateur admin pour tests."""
    with app.app_context():
        user = User(username="admin", email="admin@test.com", role="admin")
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def operator_user(app):
    """Créer utilisateur operator pour tests."""
    with app.app_context():
        user = User(username="operator", email="operator@test.com", role="operator")
        user.set_password("operator")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_token(client, admin_user):
    """Obtenir token JWT pour admin."""
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin"}
    )
    return response.json["token"]


class TestApiConfigBlueprint:
    """Tests pour le blueprint API Config."""

    def test_list_api_configs(self, client, auth_token, app, admin_user):
        """Test liste configs APIs."""
        with app.app_context():
            # Créer config API
            api_config = ApiConfig(
                user_id=admin_user.id,
                api_name="omdb",
            )
            api_config.set_api_key({"api_key": "test_key"})
            db.session.add(api_config)
            db.session.commit()

        response = client.get(
            "/api/config/apis", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "api_configs" in data
        assert len(data["api_configs"]) >= 1

    def test_create_api_config(self, client, auth_token, app, admin_user):
        """Test création config API."""
        response = client.post(
            "/api/config/apis",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"api_name": "omdb", "api_data": {"api_key": "test_omdb_key"}},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "api_config" in data
        assert data["api_config"]["api_name"] == "omdb"

    def test_get_api_config(self, client, auth_token, app, admin_user):
        """Test récupération config API."""
        with app.app_context():
            api_config = ApiConfig(
                user_id=admin_user.id,
                api_name="tvdb",
            )
            api_config.set_api_key({"api_key": "test_tvdb_key"})
            db.session.add(api_config)
            db.session.commit()

        response = client.get(
            "/api/config/apis/tvdb", headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "api_config" in data
        assert data["api_config"]["api_name"] == "tvdb"
        # Clé API ne doit pas être exposée en clair
        assert "api_key" not in data["api_config"] or "***" in str(data["api_config"])

    def test_update_api_config(self, client, auth_token, app, admin_user):
        """Test mise à jour config API."""
        with app.app_context():
            api_config = ApiConfig(
                user_id=admin_user.id,
                api_name="tmdb",
            )
            api_config.set_api_key({"api_key": "old_key"})
            db.session.add(api_config)
            db.session.commit()

        response = client.put(
            "/api/config/apis/tmdb",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"api_data": {"api_key": "new_key"}},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_delete_api_config(self, client, auth_token, app, admin_user):
        """Test suppression config API."""
        with app.app_context():
            api_config = ApiConfig(
                user_id=admin_user.id,
                api_name="openlibrary",
            )
            api_config.set_api_key({"api_key": "test_key"})
            db.session.add(api_config)
            db.session.commit()

        response = client.delete(
            "/api/config/apis/openlibrary",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_test_api_connection(self, client, auth_token, app, admin_user):
        """Test connexion API."""
        with app.app_context():
            api_config = ApiConfig(
                user_id=admin_user.id,
                api_name="omdb",
            )
            api_config.set_api_key({"api_key": "test_key"})
            db.session.add(api_config)
            db.session.commit()

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"Response": "True"}

            response = client.post(
                "/api/config/apis/omdb/test",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_api_config_requires_auth(self, client, app):
        """Test que les endpoints nécessitent authentification."""
        response = client.get("/api/config/apis")
        assert response.status_code == 401

    def test_delete_requires_admin(self, client, app, operator_user):
        """Test que suppression nécessite admin."""
        # Login operator
        login_response = client.post(
            "/api/auth/login", json={"username": "operator", "password": "operator"}
        )
        operator_token = login_response.json["token"]

        response = client.delete(
            "/api/config/apis/omdb",
            headers={"Authorization": f"Bearer {operator_token}"},
        )

        # Devrait être refusé pour operator (403)
        assert response.status_code in [403, 401]
