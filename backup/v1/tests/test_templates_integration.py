"""
Tests d'intégration pour le système de templates NFO.

Valide que les templates DB sont bien utilisés dans le packaging.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from web.app import create_app
from web.database import db
from web.models.template import NfoTemplate
from web.models.user import User, UserRole
from web.services.template_renderer import render_nfo_template


@pytest.fixture
def app():
    """Créer une instance Flask pour les tests."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Créer un utilisateur de test."""
    with app.app_context():
        user = User(
            username="test_user",
            email="test@example.com",
            role=UserRole.ADMIN,
        )
        user.set_password("test_password")
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def test_template(app, test_user):
    """Créer un template NFO de test."""
    with app.app_context():
        template = NfoTemplate(
            name="test_template",
            description="Template de test",
            content="""Title: {{title}}
Author: {{author}}
{{#if isbn}}ISBN: {{isbn}}{{/if}}
Release: {{release_name}}""",
            is_default=False,
            created_by=test_user.id,
        )
        db.session.add(template)
        db.session.commit()
        yield template


class TestTemplateIntegration:
    """Tests d'intégration templates NFO."""

    def test_template_rendering_with_conditionals(self, test_template):
        """
        Test : Rendu template avec conditionnelles.
        """
        variables = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890",
            "release_name": "test.book.2023.epub-testgrp",
        }

        result = render_nfo_template(test_template.content, variables)

        assert "Title: Test Book" in result
        assert "Author: Test Author" in result
        assert "ISBN: 1234567890" in result
        assert "Release: test.book.2023.epub-testgrp" in result

    def test_template_rendering_without_optional_fields(self, test_template):
        """
        Test : Rendu template sans champs optionnels (conditionnelles).
        """
        variables = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "",  # Vide
            "release_name": "test.book.2023.epub-testgrp",
        }

        result = render_nfo_template(test_template.content, variables)

        assert "Title: Test Book" in result
        assert "ISBN:" not in result  # Conditionnelle exclue
