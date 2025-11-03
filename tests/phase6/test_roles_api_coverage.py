"""Additional tests for Roles API to reach ≥90% coverage."""

from __future__ import annotations

from web.extensions import db
from web.models import Permission, Role, User


def test_list_roles_with_name_filter(client, app):
    """Test listing roles with name filter."""
    with app.app_context():
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        role1 = Role(name="Admin", description="Administrator")
        role2 = Role(name="Editor", description="Editor")
        db.session.add_all([role1, role2])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/roles?name=Admin", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert all("Admin" in r["name"] for r in data["roles"])


def test_get_role_not_found(client, app):
    """Test getting non-existent role."""
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

        response = client.get("/api/roles/99999", headers=headers)
        assert response.status_code == 404


def test_create_role_missing_name(client, app):
    """Test creating role with missing name."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/roles",
            json={"description": "Test"},
            headers=headers,
        )
        assert response.status_code == 400


def test_create_role_no_data(client, app):
    """Test creating role with no data."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = client.post("/api/roles", json={}, headers=headers)
        assert response.status_code == 400


def test_create_role_duplicate_name(client, app):
    """Test creating role with duplicate name."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        role = Role(name="ExistingRole")
        db.session.add(role)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/roles",
            json={"name": "ExistingRole"},
            headers=headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.get_json()["message"].lower()


def test_create_role_with_permissions(client, app):
    """Test creating role with permissions."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        perm1 = Permission.query.filter_by(resource="releases", action="read").first()
        if not perm1:
            perm1 = Permission(resource="releases", action="read")
            db.session.add(perm1)
        perm2 = Permission.query.filter_by(resource="releases", action="write").first()
        if not perm2:
            perm2 = Permission(resource="releases", action="write")
            db.session.add(perm2)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/roles",
            json={
                "name": "Editor",
                "permission_ids": [perm1.id, perm2.id],
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.get_json()
        assert len(data["role"]["permissions"]) == 2


def test_update_role_not_found(client, app):
    """Test updating non-existent role."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            "/api/roles/99999",
            json={"name": "Updated"},
            headers=headers,
        )
        assert response.status_code == 404


def test_update_role_no_data(client, app):
    """Test updating role with no data."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        role = Role(name="TestRole")
        db.session.add(role)
        db.session.commit()
        role_id = role.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = client.put(
            f"/api/roles/{role_id}",
            json={},
            headers=headers,
        )
        assert response.status_code == 400


def test_update_role_duplicate_name(client, app):
    """Test updating role with duplicate name."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        role1 = Role(name="Role1")
        role2 = Role(name="Role2")
        db.session.add_all([role1, role2])
        db.session.commit()
        role2_id = role2.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            f"/api/roles/{role2_id}",
            json={"name": "Role1"},
            headers=headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.get_json()["message"].lower()


def test_update_role_with_permissions(client, app):
    """Test updating role with permissions."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="testuser", email="test@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        role = Role(name="TestRole")
        perm1 = Permission.query.filter_by(resource="releases", action="read").first()
        if not perm1:
            perm1 = Permission(resource="releases", action="read")
            db.session.add(perm1)
        perm2 = Permission.query.filter_by(resource="releases", action="write").first()
        if not perm2:
            perm2 = Permission(resource="releases", action="write")
            db.session.add(perm2)
        db.session.add(role)
        db.session.commit()
        role_id = role.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            f"/api/roles/{role_id}",
            json={"permission_ids": [perm1.id, perm2.id]},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["role"]["permissions"]) == 2


def test_delete_role_not_found(client, app):
    """Test deleting non-existent role."""
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

        response = client.delete("/api/roles/99999", headers=headers)
        assert response.status_code == 404
