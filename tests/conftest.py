"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pytest

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Conditional import for Flask fixtures (only if web/ exists)
_web_exists = (project_root / "web").exists()
if _web_exists:
    try:
        from web.app import create_app
        from web.extensions import db
    except ImportError:
        _web_exists = False


@pytest.fixture
def app(tmp_path: Path) -> Iterator["Flask"]:
    """Flask application configured for tests.
    
    Only available if web/ module exists.
    """
    if not _web_exists:
        pytest.skip("web/ module not available (Phase 0 only)")
    
    os.environ["TEST_DB_PATH"] = str(tmp_path / "pytest.sqlite")
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    os.environ.pop("TEST_DB_PATH", None)


@pytest.fixture
def client(app: "Flask") -> "FlaskClient":
    """Flask test client.
    
    Only available if web/ module exists.
    """
    if not _web_exists:
        pytest.skip("web/ module not available (Phase 0 only)")
    return app.test_client()


@pytest.fixture
def auth_headers(app: "Flask") -> dict[str, str]:
    """Default authentication headers (filled in tests as needed).
    
    Only available if web/ module exists.
    """
    if not _web_exists:
        pytest.skip("web/ module not available (Phase 0 only)")
    return {}
