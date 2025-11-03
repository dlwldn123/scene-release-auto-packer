"""Tests for permissions utilities."""

from __future__ import annotations

from web.extensions import db
from web.models import Permission, Role, User
from web.utils.permissions import (
    can_manage_user,
    check_permission,
    get_user_permissions,
    is_admin,
)


def test_is_admin_with_admin_role(app):
    """Test is_admin returns True for user with admin role."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        db.session.commit()

        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        assert is_admin(user) is True


def test_is_admin_without_admin_role(app):
    """Test is_admin returns False for user without admin role."""
    with app.app_context():
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        assert is_admin(user) is False


def test_check_permission_admin_has_all(app):
    """Test check_permission returns True for admin for all resources."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        db.session.commit()

        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        assert check_permission(user, "releases", "read") is True
        assert check_permission(user, "releases", "write") is True
        assert check_permission(user, "rules", "mod") is True
        assert check_permission(user, "users", "delete") is True


def test_check_permission_user_with_role_permission(app):
    """Test check_permission returns True for user with role permission."""
    with app.app_context():
        editor_role = Role(name="editor", description="Editor")
        permission = Permission.query.filter_by(resource="releases", action="mod").first()
        if not permission:
            permission = Permission(resource="releases", action="mod")
            db.session.add(permission)
        editor_role.permissions.append(permission)
        db.session.add(editor_role)
        db.session.commit()

        user = User(username="editor", email="editor@test.com")
        user.set_password("password")
        user.roles.append(editor_role)
        db.session.add(user)
        db.session.commit()

        assert check_permission(user, "releases", "mod") is True
        assert check_permission(user, "releases", "delete") is False
        assert check_permission(user, "rules", "read") is False


def test_check_permission_user_own_release(app):
    """Test check_permission allows user to manage own releases."""
    with app.app_context():
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # User can read their own releases
        assert (
            check_permission(user, "releases", "read", release_user_id=user.id) is True
        )
        # User can write their own releases
        assert (
            check_permission(user, "releases", "write", release_user_id=user.id) is True
        )
        # User can delete their own releases
        assert (
            check_permission(user, "releases", "delete", release_user_id=user.id)
            is True
        )


def test_can_manage_user_admin_can_manage_all(app):
    """Test can_manage_user allows admin to manage all users."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        db.session.commit()

        admin_user = User(username="admin", email="admin@test.com")
        admin_user.set_password("password")
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()

        target_user = User(username="target", email="target@test.com")
        target_user.set_password("password")
        db.session.add(target_user)
        db.session.commit()

        assert can_manage_user(admin_user, target_user.id) is True


def test_can_manage_user_can_manage_self(app):
    """Test can_manage_user allows user to manage themselves."""
    with app.app_context():
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        assert can_manage_user(user, user.id) is True


def test_can_manage_user_cannot_manage_others(app):
    """Test can_manage_user prevents user from managing others."""
    with app.app_context():
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add_all([user1, user2])
        db.session.commit()

        assert can_manage_user(user1, user2.id) is False


def test_get_user_permissions_admin(app):
    """Test get_user_permissions returns all permissions for admin."""
    with app.app_context():
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
        db.session.commit()

        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()

        permissions = get_user_permissions(user)

        assert "releases" in permissions
        assert "read" in permissions["releases"]
        assert "write" in permissions["releases"]
        assert "mod" in permissions["releases"]
        assert "delete" in permissions["releases"]


def test_get_user_permissions_user_with_role(app):
    """Test get_user_permissions returns permissions from role."""
    with app.app_context():
        editor_role = Role(name="editor", description="Editor")
        permission_read = Permission.query.filter_by(resource="releases", action="read").first()
        if not permission_read:
            permission_read = Permission(resource="releases", action="read")
            db.session.add(permission_read)
        permission_mod = Permission.query.filter_by(resource="releases", action="mod").first()
        if not permission_mod:
            permission_mod = Permission(resource="releases", action="mod")
            db.session.add(permission_mod)
        editor_role.permissions.extend([permission_read, permission_mod])
        db.session.add(editor_role)
        db.session.commit()

        user = User(username="editor", email="editor@test.com")
        user.set_password("password")
        user.roles.append(editor_role)
        db.session.add(user)
        db.session.commit()

        permissions = get_user_permissions(user)

        assert "releases" in permissions
        assert "read" in permissions["releases"]
        assert "mod" in permissions["releases"]
        assert "write" not in permissions["releases"]
        assert "delete" not in permissions["releases"]


def test_get_user_permissions_user_without_permissions(app):
    """Test get_user_permissions adds READ for releases even without permissions."""
    with app.app_context():
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        permissions = get_user_permissions(user)

        # Should have READ on releases even without role permissions
        assert "releases" in permissions
        assert "read" in permissions["releases"]
        assert len(permissions["releases"]) == 1


def test_get_user_permissions_user_with_role_no_releases_permission(app):
    """Test get_user_permissions adds READ for releases if role has no releases permission."""
    with app.app_context():
        rules_role = Role(name="rules_only", description="Rules only")
        permission_read_rules = Permission.query.filter_by(resource="rules", action="read").first()
        if not permission_read_rules:
            permission_read_rules = Permission(resource="rules", action="read")
            db.session.add(permission_read_rules)
        rules_role.permissions.append(permission_read_rules)
        db.session.add(rules_role)
        db.session.commit()

        user = User(username="user", email="user@test.com")
        user.set_password("password")
        user.roles.append(rules_role)
        db.session.add(user)
        db.session.commit()

        permissions = get_user_permissions(user)

        # Should have READ on releases even though role doesn't have it
        assert "releases" in permissions
        assert "read" in permissions["releases"]
        assert "rules" in permissions
        assert "read" in permissions["rules"]


def test_check_permission_no_permission(app):
    """Test check_permission returns False when user has no permission."""
    with app.app_context():
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # User has no roles, no permissions
        assert check_permission(user, "rules", "write") is False
        assert check_permission(user, "users", "read") is False


def test_check_permission_other_user_release(app):
    """Test check_permission returns False for other user's releases without permission."""
    with app.app_context():
        user1 = User(username="user1", email="user1@test.com")
        user1.set_password("password")
        user2 = User(username="user2", email="user2@test.com")
        user2.set_password("password")
        db.session.add_all([user1, user2])
        db.session.commit()

        # User1 cannot access user2's releases without permission
        assert (
            check_permission(user1, "releases", "read", release_user_id=user2.id)
            is False
        )
        assert (
            check_permission(user1, "releases", "write", release_user_id=user2.id)
            is False
        )


def test_check_permission_release_different_actions(app):
    """Test check_permission with different actions on own releases."""
    with app.app_context():
        user = User(username="user", email="user@test.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # User can perform all actions on own releases
        assert (
            check_permission(user, "releases", "read", release_user_id=user.id) is True
        )
        assert (
            check_permission(user, "releases", "write", release_user_id=user.id) is True
        )
        assert (
            check_permission(user, "releases", "mod", release_user_id=user.id) is True
        )
        assert (
            check_permission(user, "releases", "delete", release_user_id=user.id)
            is True
        )


def test_require_permission_placeholder(app):
    """Test require_permission placeholder function."""
    from web.utils.permissions import require_permission

    # This is a placeholder function that always returns True
    assert require_permission("releases", "read") is True
    assert require_permission("rules", "write", require_admin=True) is True


def test_create_default_permissions_empty_db(app):
    """Test create_default_permissions creates all default permissions."""
    from web.utils.permissions import create_default_permissions
    from web.models import Permission

    with app.app_context():
        # Ensure no permissions exist
        Permission.query.delete()
        db.session.commit()

        # Create default permissions
        create_default_permissions()

        # Verify all permissions were created
        permissions = Permission.query.all()
        assert len(permissions) == 20  # 5 resources * 4 actions

        # Verify specific permissions exist
        assert (
            Permission.query.filter_by(resource="releases", action="read").first()
            is not None
        )
        assert (
            Permission.query.filter_by(resource="rules", action="write").first()
            is not None
        )
        assert (
            Permission.query.filter_by(resource="users", action="delete").first()
            is not None
        )
        assert (
            Permission.query.filter_by(resource="config", action="mod").first()
            is not None
        )


def test_create_default_permissions_existing_permissions(app):
    """Test create_default_permissions skips existing permissions."""
    from web.utils.permissions import create_default_permissions
    from web.models import Permission

    with app.app_context():
        # Delete all permissions first
        Permission.query.delete()
        db.session.commit()
        
        # Create one permission manually
        existing_perm = Permission(resource="releases", action="read")
        db.session.add(existing_perm)
        db.session.commit()

        initial_count = Permission.query.count()

        # Create default permissions
        create_default_permissions()

        # Should have added 19 more (not 20, since one already existed)
        final_count = Permission.query.count()
        assert final_count == initial_count + 19

        # Original permission should still exist
        existing = Permission.query.filter_by(
            resource="releases", action="read"
        ).first()
        assert existing is not None
        assert existing.id == existing_perm.id
