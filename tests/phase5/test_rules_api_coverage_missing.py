"""Additional tests for Rules API to achieve ≥90% coverage."""

from __future__ import annotations

from unittest.mock import Mock, patch

from web.extensions import db
from web.models import Permission, Role, Rule, User


def test_list_rules_user_not_found(client) -> None:
    """Test listing rules with invalid user (404)."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete user to simulate user not found
    with client.application.app_context():
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    # Try to list rules - should fail with 401/404
    response = client.get(
        "/api/rules",
        headers={"Authorization": f"Bearer {token}"},
    )
    # JWT token is valid but user doesn't exist anymore
    assert response.status_code in [404, 401]


def test_list_scenerules_rules_user_not_found(client) -> None:
    """Test listing scenerules with invalid user (404)."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete user to simulate user not found
    with client.application.app_context():
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    # Try to list scenerules - should fail
    response = client.get(
        "/api/rules/scenerules",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in [404, 401]


def test_list_scenerules_rules_with_filters(client) -> None:
    """Test listing scenerules with scene/year filters."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List with scene filter
    response = client.get(
        "/api/rules/scenerules?scene=English",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "rules" in data
    # All known rules are English by default
    assert len(data["rules"]) > 0

    # List with year filter
    response = client.get(
        "/api/rules/scenerules?year=2022",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "rules" in data


def test_download_scenerules_rule_user_not_found(client) -> None:
    """Test downloading scenerules rule with invalid user (404)."""
    with client.application.app_context():
        db.create_all()
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete user to simulate user not found
    with client.application.app_context():
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    # Try to download rule - should fail
    response = client.post(
        "/api/rules/scenerules/download",
        headers={"Authorization": f"Bearer {token}"},
        json={"section": "eBOOK", "year": 2022},
    )
    assert response.status_code in [404, 401]


def test_download_scenerules_rule_permission_denied(client) -> None:
    """Test downloading scenerules rule without write permission (403)."""
    with client.application.app_context():
        db.create_all()
        # Create user without write permission
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Try to download rule - should fail with permission denied
    response = client.post(
        "/api/rules/scenerules/download",
        headers={"Authorization": f"Bearer {token}"},
        json={"section": "eBOOK", "year": 2022},
    )
    assert response.status_code == 403
    assert response.get_json()["message"] == "Permission denied"


def test_download_scenerules_rule_no_data(client) -> None:
    """Test downloading scenerules rule without data (400)."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Try to download without data
    response = client.post(
        "/api/rules/scenerules/download",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data="{}",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data is not None
    assert data["message"] == "No data provided"


def test_download_scenerules_rule_missing_section(client) -> None:
    """Test downloading scenerules rule without section (400)."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Try to download without section
    response = client.post(
        "/api/rules/scenerules/download",
        headers={"Authorization": f"Bearer {token}"},
        json={"year": 2022},
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "Section is required"


def test_download_scenerules_rule_by_url(client) -> None:
    """Test downloading scenerules rule by URL."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Mock the download service
    with patch("web.services.scenerules_download.ScenerulesDownloadService.download_rule_by_url") as mock_download:
        mock_download.return_value = {
            "name": "[2022] eBOOK",
            "content": "Test content",
            "section": "eBOOK",
            "year": 2022,
            "scene": "English",
            "source": "scenerules.org",
            "url": "https://scenerules.org/nfo/2022_eBOOK.nfo",
        }

        response = client.post(
            "/api/rules/scenerules/download",
            headers={"Authorization": f"Bearer {token}"},
            json={"url": "https://scenerules.org/nfo/2022_eBOOK.nfo"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "rule" in data
        assert data["rule"]["section"] == "eBOOK"


def test_download_scenerules_rule_update_existing(client) -> None:
    """Test downloading scenerules rule updates existing."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        # Create existing rule
        existing_rule = Rule(
            name="Old Name",
            content="Old content",
            section="eBOOK",
            year=2022,
            scene="English",
        )
        db.session.add(existing_rule)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Mock the download service
    with patch("web.services.scenerules_download.ScenerulesDownloadService.download_rule") as mock_download:
        mock_download.return_value = {
            "name": "[2022] eBOOK",
            "content": "New content",
            "section": "eBOOK",
            "year": 2022,
            "scene": "English",
            "source": "scenerules.org",
        }

        response = client.post(
            "/api/rules/scenerules/download",
            headers={"Authorization": f"Bearer {token}"},
            json={"section": "eBOOK", "year": 2022},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "rule" in data
        assert data["was_existing"] is True
        assert data["rule"]["content"] == "New content"


def test_download_scenerules_rule_value_error(client) -> None:
    """Test downloading scenerules rule with ValueError (404)."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Mock the download service to raise ValueError
    with patch("web.services.scenerules_download.ScenerulesDownloadService.download_rule") as mock_download:
        mock_download.side_effect = ValueError("Rule not found: NONEXISTENT [2022]")

        response = client.post(
            "/api/rules/scenerules/download",
            headers={"Authorization": f"Bearer {token}"},
            json={"section": "NONEXISTENT", "year": 2022},
        )
        assert response.status_code == 404
        assert "not found" in response.get_json()["message"].lower()


def test_download_scenerules_rule_general_exception(client) -> None:
    """Test downloading scenerules rule with general exception (500)."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_permission = db.session.query(Permission).filter_by(
            resource="rules", action="write"
        ).first()
        if not write_permission:
            write_permission = Permission(resource="rules", action="write")
            db.session.add(write_permission)
        
        admin_role.permissions.append(write_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Mock the download service to raise generic Exception
    with patch("web.services.scenerules_download.ScenerulesDownloadService.download_rule") as mock_download:
        mock_download.side_effect = Exception("Network error")

        response = client.post(
            "/api/rules/scenerules/download",
            headers={"Authorization": f"Bearer {token}"},
            json={"section": "eBOOK", "year": 2022},
        )
        assert response.status_code == 500
        assert "Failed to download rule" in response.get_json()["message"]


def test_upload_rule_user_not_found(client) -> None:
    """Test uploading rule with invalid user (404)."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete user to simulate user not found
    with client.application.app_context():
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    # Create a dummy file
    from io import BytesIO
    file_content = BytesIO(b"Test NFO content")
    file_content.name = "test.nfo"

    # Try to upload rule - should fail
    response = client.post(
        "/api/rules/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"file": (file_content, "test.nfo")},
    )
    assert response.status_code in [404, 401]


def test_upload_rule_invalid_encoding(client) -> None:
    """Test uploading rule with invalid encoding (400)."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Create file with invalid encoding (binary that can't be decoded as UTF-8 or ISO-8859-1)
    from io import BytesIO
    # Use bytes that are invalid in both UTF-8 and ISO-8859-1
    content = b"\xff\xfe\xfd\xfc"  # Invalid bytes
    file_content = BytesIO(content)
    file_content.name = "test.nfo"

    # Upload rule - should fail with invalid encoding
    response = client.post(
        "/api/rules/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"file": (file_content, "test.nfo")},
    )
    assert response.status_code == 400
    assert "Invalid file encoding" in response.get_json()["message"]
