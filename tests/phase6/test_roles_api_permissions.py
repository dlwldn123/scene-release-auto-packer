"""Tests for roles API with permissions."""

from __future__ import annotations

from web.extensions import db
from web.models import Permission, Role, User


def test_list_roles_all_authenticated(client, app):
    """Test any authenticated user can list roles."""
    with app.app_context():
        user = User(username="viewer", email="viewer@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "viewer", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/roles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "roles" in response.get_json()


def test_create_role_admin_success(client, app):
    """Test admin can create role."""
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
        "/api/roles",
        json={"name": "newrole", "description": "New Role"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.get_json()["role"]["name"] == "newrole"


def test_create_role_viewer_permission_denied(client, app):
    """Test viewer without write permission cannot create role."""
    with app.app_context():
        viewer_role = Role(name="viewer", description="Viewer")
        permission_read = Permission.query.filter_by(resource="roles", action="read").first()
        if permission_read:
            viewer_role.permissions.append(permission_read)
        viewer_user = User(username="viewer", email="viewer@test.com")
        viewer_user.set_password("password")
        viewer_user.roles.append(viewer_role)
        db.session.add_all([viewer_role, viewer_user])
        db.session.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "viewer", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/roles",
        json={"name": "newrole", "description": "New Role"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "permission denied" in response.get_json()["message"].lower()


def test_update_role_admin_success(client, app):
    """Test admin can update role."""
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
        
        role = Role(name="testrole", description="Test Role")
        db.session.add(role)
        db.session.commit()
        role_id = role.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/roles/{role_id}",
        json={"name": "updatedrole"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["role"]["name"] == "updatedrole"


def test_update_role_viewer_permission_denied(client, app):
    """Test viewer cannot update role."""
    with app.app_context():
        viewer_role = Role(name="viewer", description="Viewer")
        permission_read = Permission.query.filter_by(resource="roles", action="read").first()
        if permission_read:
            viewer_role.permissions.append(permission_read)
        viewer_user = User(username="viewer", email="viewer@test.com")
        viewer_user.set_password("password")
        viewer_user.roles.append(viewer_role)
        role = Role(name="testrole", description="Test Role")
        db.session.add_all([viewer_role, viewer_user, role])
        db.session.commit()
        role_id = role.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "viewer", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/roles/{role_id}",
        json={"name": "updatedrole"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_delete_role_admin_success(client, app):
    """Test admin can delete role."""
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
        
        role = Role(name="testrole", description="Test Role")
        db.session.add(role)
        db.session.commit()
        role_id = role.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.delete(
        f"/api/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"].lower()


def test_delete_role_viewer_permission_denied(client, app):
    """Test viewer cannot delete role."""
    with app.app_context():
        viewer_role = Role(name="viewer", description="Viewer")
        permission_read = Permission.query.filter_by(resource="roles", action="read").first()
        if permission_read:
            viewer_role.permissions.append(permission_read)
        viewer_user = User(username="viewer", email="viewer@test.com")
        viewer_user.set_password("password")
        viewer_user.roles.append(viewer_role)
        role = Role(name="testrole", description="Test Role")
        db.session.add_all([viewer_role, viewer_user, role])
        db.session.commit()
        role_id = role.id
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": "viewer", "password": "password"},
    )
    token = login_response.get_json()["access_token"]

    response = client.delete(
        f"/api/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
