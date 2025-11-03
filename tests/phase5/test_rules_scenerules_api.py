"""Tests for Rules API scenerules.org endpoints."""

from __future__ import annotations

from unittest.mock import Mock, patch

from web.extensions import db
from web.models import Permission, Role, Rule, User


def test_list_scenerules_rules(client, app):
    """Test list_scenerules_rules success."""
    with app.app_context():
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/rules/scenerules", headers=headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "rules" in data
        assert "total" in data
        assert isinstance(data["rules"], list)
        assert len(data["rules"]) > 0


def test_list_scenerules_rules_with_filters(client, app):
    """Test list_scenerules_rules with filters."""
    with app.app_context():
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Filter by section
        response = client.get(
            "/api/rules/scenerules?section=eBOOK", headers=headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert all(r["section"] == "eBOOK" for r in data["rules"])

        # Filter by year
        response = client.get("/api/rules/scenerules?year=2022", headers=headers)

        assert response.status_code == 200
        data = response.get_json()
        assert all(r["year"] == 2022 for r in data["rules"])


def test_list_scenerules_rules_with_local_indicator(client, app):
    """Test list_scenerules_rules shows is_downloaded indicator."""
    with app.app_context():
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # Create a local rule matching scenerules.org rule
        local_rule = Rule(
            name="[2022] eBOOK",
            content="Local rule content",
            section="eBOOK",
            year=2022,
            scene="English",
        )
        db.session.add(local_rule)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/rules/scenerules", headers=headers)

        assert response.status_code == 200
        data = response.get_json()

        # Find eBOOK rule
        ebook_rule = next(
            (r for r in data["rules"] if r["section"] == "eBOOK"), None
        )
        assert ebook_rule is not None
        assert ebook_rule["is_downloaded"] is True
        assert ebook_rule["local_rule_id"] == local_rule.id


def test_download_scenerules_rule_success(client, app):
    """Test download_scenerules_rule success."""
    with app.app_context():
        # Create admin role with write permission
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Mock downloader
        mock_rule_data = {
            "name": "[2022] eBOOK",
            "content": "Rule content from scenerules.org",
            "section": "eBOOK",
            "year": 2022,
            "scene": "English",
            "source": "scenerules.org",
            "url": "https://scenerules.org/nfo/2022_eBOOK.nfo",
        }

        with patch(
            "web.blueprints.rules.ScenerulesDownloadService"
        ) as mock_service_class:
            mock_service = Mock()
            mock_service.download_rule.return_value = mock_rule_data
            mock_service_class.return_value = mock_service

            response = client.post(
                "/api/rules/scenerules/download",
                headers=headers,
                json={"section": "eBOOK", "year": 2022},
            )

            assert response.status_code == 201
            data = response.get_json()
            assert "rule" in data
            assert data["rule"]["name"] == "[2022] eBOOK"
            assert data["rule"]["section"] == "eBOOK"
            assert data["was_existing"] is False


def test_download_scenerules_rule_update_existing(client, app):
    """Test download_scenerules_rule updates existing rule."""
    with app.app_context():
        # Create admin role with write permission
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        # Create existing rule
        existing_rule = Rule(
            name="[2022] eBOOK (old)",
            content="Old content",
            section="eBOOK",
            year=2022,
            scene="English",
        )
        db.session.add(existing_rule)
        db.session.commit()
        rule_id = existing_rule.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Mock downloader
        mock_rule_data = {
            "name": "[2022] eBOOK",
            "content": "New content from scenerules.org",
            "section": "eBOOK",
            "year": 2022,
            "scene": "English",
            "source": "scenerules.org",
            "url": "https://scenerules.org/nfo/2022_eBOOK.nfo",
        }

        with patch(
            "web.blueprints.rules.ScenerulesDownloadService"
        ) as mock_service_class:
            mock_service = Mock()
            mock_service.download_rule.return_value = mock_rule_data
            mock_service_class.return_value = mock_service

            response = client.post(
                "/api/rules/scenerules/download",
                headers=headers,
                json={"section": "eBOOK", "year": 2022},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["rule"]["id"] == rule_id
            assert data["rule"]["content"] == "New content from scenerules.org"
            assert data["was_existing"] is True


def test_download_scenerules_rule_missing_section(client, app):
    """Test download_scenerules_rule without section returns 400."""
    with app.app_context():
        # Create admin role with write permission
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/rules/scenerules/download",
            headers=headers,
            json={},
        )

        assert response.status_code == 400
        message = response.get_json()["message"].lower()
        # Could be "no data provided" or "section is required"
        assert "section" in message or "no data" in message


def test_download_scenerules_rule_by_url(client, app):
    """Test download_scenerules_rule using URL."""
    with app.app_context():
        # Create admin role with write permission
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Mock downloader
        mock_rule_data = {
            "name": "[2022] eBOOK",
            "content": "Rule content",
            "section": "eBOOK",
            "year": 2022,
            "scene": "English",
            "source": "scenerules.org",
            "url": "https://scenerules.org/nfo/2022_eBOOK.nfo",
        }

        with patch(
            "web.blueprints.rules.ScenerulesDownloadService"
        ) as mock_service_class:
            mock_service = Mock()
            mock_service.download_rule_by_url.return_value = mock_rule_data
            mock_service_class.return_value = mock_service

            response = client.post(
                "/api/rules/scenerules/download",
                headers=headers,
                json={"url": "https://scenerules.org/nfo/2022_eBOOK.nfo"},
            )

            assert response.status_code == 201
            data = response.get_json()
            assert "rule" in data
