"""Tests for users API with permissions."""

from __future__ import annotations

from web.extensions import db
from web.models import Permission, Role, User


def test_list_users_admin_success(client, app):
    """Test admin can list users."""
    with app.app_context():
        admin_role = db.session.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        
        admin_user = db.session.query(User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", email="admin@test.com")
            admin_user.set_password("password")
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "users" in response.get_json()


def test_list_users_editor_permission_denied(client, app):
    """Test editor without read permission cannot list users."""
    with app.app_context():
        editor_role = Role(name="editor", description="Editor")
        permission_read = Permission.query.filter_by(resource="releases", action="read").first()
        if permission_read:
            editor_role.permissions.append(permission_read)
        editor_user = User(username="editor", email="editor@test.com")
        editor_user.set_password("password")
        editor_user.roles.append(editor_role)
        db.session.add_all([editor_role, editor_user])
        db.session.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "editor", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Editor has read on releases, not users
    assert response.status_code == 403


def test_create_user_admin_success(client, app):
    """Test admin can create user."""
    with app.app_context():
        admin_role = db.session.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        
        admin_user = db.session.query(User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", email="admin@test.com")
            admin_user.set_password("password")
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "securepass123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.get_json()["user"]["username"] == "newuser"


def test_create_user_editor_permission_denied(client, app):
    """Test editor without write permission cannot create user."""
    with app.app_context():
        editor_role = Role(name="editor", description="Editor")
        permission_read = Permission.query.filter_by(resource="users", action="read").first()
        if permission_read:
            editor_role.permissions.append(permission_read)
        editor_user = User(username="editor", email="editor@test.com")
        editor_user.set_password("password")
        editor_user.roles.append(editor_role)
        db.session.add_all([editor_role, editor_user])
        db.session.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "editor", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "securepass123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "permission denied" in response.get_json()["message"].lower()


def test_update_user_admin_success(client, app):
    """Test admin can update any user."""
    with app.app_context():
        admin_role = db.session.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        
        admin_user = db.session.query(User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", email="admin@test.com")
            admin_user.set_password("password")
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
        
        target_user = User(username="target", email="target@test.com")
        target_user.set_password("password")
        db.session.add(target_user)
        db.session.commit()
        target_user_id = target_user.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/users/{target_user_id}",
        json={"username": "updateduser"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == "updateduser"


def test_update_user_self_allowed(client, app):
    """Test user can update themselves."""
    with app.app_context():
        user = User(username="selfuser", email="self@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "selfuser", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/users/{user_id}",
        json={"note": "Updated note"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


def test_update_user_cannot_change_own_roles(client, app):
    """Test user cannot change their own roles."""
    with app.app_context():
        user = User(username="selfuser", email="self@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "selfuser", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/users/{user_id}",
        json={"role_ids": [1]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "cannot change your own roles" in response.get_json()["message"].lower()


def test_update_user_other_permission_denied(client, app):
    """Test editor cannot update other users."""
    with app.app_context():
        editor_role = Role(name="editor", description="editoor")
        permission_read = Permission.query.filter_by(resource="users", action="read").first()
        if permission_read:
            editor_role.permissions.append(permission_read)
        editor_user = User(username="editor", email="editor@test.com")
        editor_user.set_password("password")
        editor_user.roles.append(editor_role)
        target_user = User(username="target", email="target@test.com")
        target_user.set_password("password")
        db.session.add_all([editor_role, editor_user, target_user])
        db.session.commit()
        target_user_id = target_user.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "editor", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/users/{target_user_id}",
        json={"username": "updateduser"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_delete_user_admin_success(client, app):
    """Test admin can delete user."""
    with app.app_context():
        admin_role = db.session.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        
        admin_user = db.session.query(User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", email="admin@test.com")
            admin_user.set_password("password")
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
        
        target_user = User(username="target", email="target@test.com")
        target_user.set_password("password")
        db.session.add(target_user)
        db.session.commit()
        target_user_id = target_user.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.delete(
        f"/api/users/{target_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"].lower()


def test_delete_user_admin_cannot_delete_self(client, app):
    """Test admin cannot delete themselves."""
    with app.app_context():
        admin_role = db.session.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        
        admin_user = db.session.query(User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", email="admin@test.com")
            admin_user.set_password("password")
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
        admin_user_id = admin_user.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.delete(
        f"/api/users/{admin_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "cannot delete yourself" in response.get_json()["message"].lower()


def test_delete_user_editor_permission_denied(client, app):
    """Test editor cannot delete users."""
    with app.app_context():
        editor_role = Role(name="editor", description="Editor")
        permission_read = Permission.query.filter_by(resource="users", action="read").first()
        if permission_read:
            editor_role.permissions.append(permission_read)
        editor_user = User(username="editor", email="editor@test.com")
        editor_user.set_password("password")
        editor_user.roles.append(editor_role)
        target_user = User(username="target", email="target@test.com")
        target_user.set_password("password")
        db.session.add_all([editor_role, editor_user, target_user])
        db.session.commit()
        target_user_id = target_user.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "editor", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.delete(
        f"/api/users/{target_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
