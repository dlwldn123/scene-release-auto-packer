"""Tests for Configurations API."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Configuration, Permission, Role, User


def test_list_configurations(client) -> None:
    """Test listing configurations."""
    with client.application.app_context():
        db.create_all()
        # Create admin role and assign to user
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        # Get or create permissions
        read_config_permission = db.session.query(Permission).filter_by(
            resource="config", action="read"
        ).first()
        if not read_config_permission:
            read_config_permission = Permission(resource="config", action="read")
            db.session.add(read_config_permission)
        
        admin_role.permissions.append(read_config_permission)
        
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        config1 = Configuration(key="app.name", value="Scene Packer", category="app")
        config2 = Configuration(key="app.version", value="2.0.0", category="app")
        db.session.add_all([config1, config2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List configurations
    response = client.get(
        "/api/config",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "configurations" in data
    assert "pagination" in data
    assert len(data["configurations"]) >= 2


def test_list_configurations_with_filters(client) -> None:
    """Test listing configurations with filters."""
    with client.application.app_context():
        db.create_all()
        # Create admin role and assign to user
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        read_config_permission = db.session.query(Permission).filter_by(
            resource="config", action="read"
        ).first()
        if not read_config_permission:
            read_config_permission = Permission(resource="config", action="read")
            db.session.add(read_config_permission)
        
        admin_role.permissions.append(read_config_permission)
        
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        config1 = Configuration(key="app.name", value="Scene Packer", category="app")
        config2 = Configuration(key="db.host", value="localhost", category="database")
        db.session.add_all([config1, config2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List configurations filtered by category
    response = client.get(
        "/api/config?category=app",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["configurations"]) == 1
    assert data["configurations"][0]["category"] == "app"


def test_get_configuration(client) -> None:
    """Test getting configuration by ID."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        config = Configuration(key="app.name", value="Scene Packer", category="app")
        db.session.add(config)
        db.session.commit()
        config_id = config.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Get configuration
    response = client.get(
        f"/api/config/{config_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "configuration" in data
    assert data["configuration"]["id"] == config_id


def test_get_configuration_by_key(client) -> None:
    """Test getting configuration by key."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        config = Configuration(key="app.name", value="Scene Packer", category="app")
        db.session.add(config)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Get configuration by key
    response = client.get(
        "/api/config/key/app.name",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["configuration"]["key"] == "app.name"


def test_create_configuration(client) -> None:
    """Test creating configuration."""
    with client.application.app_context():
        db.create_all()
        # Create admin role and assign to user
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_config_permission = db.session.query(Permission).filter_by(
            resource="config", action="write"
        ).first()
        if not write_config_permission:
            write_config_permission = Permission(resource="config", action="write")
            db.session.add(write_config_permission)
        
        admin_role.permissions.append(write_config_permission)
        
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

    # Create configuration
    response = client.post(
        "/api/config",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": "app.debug",
            "value": "false",
            "category": "app",
            "description": "Debug mode",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "configuration" in data
    assert data["configuration"]["key"] == "app.debug"


def test_update_configuration(client) -> None:
    """Test updating configuration."""
    with client.application.app_context():
        db.create_all()
        # Create admin role and assign to user
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        write_config_permission = db.session.query(Permission).filter_by(
            resource="config", action="write"
        ).first()
        if not write_config_permission:
            write_config_permission = Permission(resource="config", action="write")
            db.session.add(write_config_permission)
        
        admin_role.permissions.append(write_config_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        config = Configuration(key="app.name", value="Scene Packer", category="app")
        db.session.add(config)
        db.session.commit()
        config_id = config.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Update configuration
    response = client.put(
        f"/api/config/{config_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "Scene Packer v2"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["configuration"]["value"] == "Scene Packer v2"


def test_delete_configuration(client) -> None:
    """Test deleting configuration."""
    with client.application.app_context():
        db.create_all()
        # Create admin role and assign to user
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        
        delete_config_permission = db.session.query(Permission).filter_by(
            resource="config", action="delete"
        ).first()
        if not delete_config_permission:
            delete_config_permission = Permission(resource="config", action="delete")
            db.session.add(delete_config_permission)
        
        admin_role.permissions.append(delete_config_permission)
        
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        config = Configuration(key="app.name", value="Scene Packer", category="app")
        db.session.add(config)
        db.session.commit()
        config_id = config.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete configuration
    response = client.delete(
        f"/api/config/{config_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(
        f"/api/config/{config_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404
