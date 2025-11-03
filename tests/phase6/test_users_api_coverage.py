"""Additional tests for Users API to reach ≥90% coverage."""

from __future__ import annotations

from web.extensions import db
from web.models import Role, User


def test_list_users_with_username_filter(client, app):
    """Test listing users with username filter."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        user1.roles.append(admin_role)
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add_all([admin_role, user1, user2])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "user1", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/users?username=user1", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert all("user1" in u["username"] for u in data["users"])


def test_list_users_with_email_filter(client, app):
    """Test listing users with email filter."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        user1.roles.append(admin_role)
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add_all([admin_role, user1, user2])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "user1", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/users?email=user1@test.com", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert all("user1@test.com" in u["email"] for u in data["users"])


def test_list_users_with_role_filter(client, app):
    """Test listing users with role filter."""
    with app.app_context():
        role = Role(name="Admin")
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        user1.roles.append(role)
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add_all([role, user1, user2])
        db.session.commit()
        role_id = role.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "user1", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/api/users?role_id={role_id}", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        # Should include user1 (has role) but might include others if pagination
        assert len(data["users"]) >= 1


def test_get_user_not_found(client, app):
    """Test getting non-existent user."""
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

        response = client.get("/api/users/99999", headers=headers)
        assert response.status_code == 404


def test_create_user_missing_fields(client, app):
    """Test creating user with missing required fields."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Missing username
        response = client.post(
            "/api/users",
            json={"email": "test@test.com", "password": "password"},
            headers=headers,
        )
        assert response.status_code == 400

        # Missing email
        response = client.post(
            "/api/users",
            json={"username": "testuser", "password": "password"},
            headers=headers,
        )
        assert response.status_code == 400

        # Missing password
        response = client.post(
            "/api/users",
            json={"username": "testuser", "email": "test@test.com"},
            headers=headers,
        )
        assert response.status_code == 400


def test_create_user_no_data(client, app):
    """Test creating user with no data."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = client.post("/api/users", json={}, headers=headers)
        assert response.status_code == 400


def test_create_user_duplicate_username(client, app):
    """Test creating user with duplicate username."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        existing = User(username="existing", email="existing@test.com")
        existing.set_password("password")
        db.session.add(existing)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/users",
            json={
                "username": "existing",
                "email": "new@test.com",
                "password": "password",
            },
            headers=headers,
        )
        assert response.status_code == 400
        assert "username already exists" in response.get_json()["message"].lower()


def test_create_user_duplicate_email(client, app):
    """Test creating user with duplicate email."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        existing = User(username="existing", email="existing@test.com")
        existing.set_password("password")
        db.session.add_all([admin_role, user, existing])
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/users",
            json={
                "username": "newuser",
                "email": "existing@test.com",
                "password": "password",
            },
            headers=headers,
        )
        assert response.status_code == 400
        assert "email already exists" in response.get_json()["message"].lower()


def test_update_user_not_found(client, app):
    """Test updating non-existent user."""
    with app.app_context():
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            "/api/users/99999",
            json={"email": "updated@test.com"},
            headers=headers,
        )
        assert response.status_code == 404


def test_update_user_no_data(client, app):
    """Test updating user with no data."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()
        user_id = user.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = client.put(
            f"/api/users/{user_id}",
            json={},
            headers=headers,
        )
        assert response.status_code == 400


def test_update_user_duplicate_username(client, app):
    """Test updating user with duplicate username."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        user1.roles.append(admin_role)
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add_all([admin_role, user1, user2])
        db.session.commit()
        user2_id = user2.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "user1", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            f"/api/users/{user2_id}",
            json={"username": "user1"},
            headers=headers,
        )
        assert response.status_code == 400
        assert "username already exists" in response.get_json()["message"].lower()


def test_update_user_duplicate_email(client, app):
    """Test updating user with duplicate email."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        user1.roles.append(admin_role)
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add_all([admin_role, user1, user2])
        db.session.commit()
        user2_id = user2.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "user1", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            f"/api/users/{user2_id}",
            json={"email": "user1@test.com"},
            headers=headers,
        )
        assert response.status_code == 400
        assert "email already exists" in response.get_json()["message"].lower()


def test_update_user_with_roles(client, app):
    """Test updating user with roles."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.roles.append(admin_role)
        target_user = User(username="target", email="target@test.com")
        target_user.set_password("password")
        role1 = Role(name="Role1")
        role2 = Role(name="Role2")
        db.session.add_all([admin_role, admin_user, target_user, role1, role2])
        db.session.commit()
        target_user_id = target_user.id

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            f"/api/users/{target_user_id}",
            json={"role_ids": [role1.id, role2.id]},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["user"]["roles"]) == 2


def test_delete_user_not_found(client, app):
    """Test deleting non-existent user."""
    with app.app_context():
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "password"},
        )
        token = login_response.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.delete("/api/users/99999", headers=headers)
        assert response.status_code == 404
