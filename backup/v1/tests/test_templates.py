"""
Tests unitaires pour le système de templates NFO (TDD - RED phase).

Ces tests valident le rendu des templates avec placeholders.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from web.models.template import NfoTemplate
from web.services.template_renderer import get_template_variables, render_nfo_template


class TestTemplateRenderer:
    """Tests pour le service de rendu de templates."""

    def test_render_simple_variables(self):
        """
        Test : Remplacement de variables simples {{variable}}.
        """
        template = "Title: {{title}}\nAuthor: {{author}}"
        variables = {
            "title": "Test Book",
            "author": "Test Author",
        }

        result = render_nfo_template(template, variables)

        assert "Test Book" in result
        assert "Test Author" in result
        assert "{{title}}" not in result
        assert "{{author}}" not in result

    def test_render_missing_variables(self):
        """
        Test : Variables manquantes remplacées par chaîne vide.
        """
        template = "Title: {{title}}\nAuthor: {{author}}"
        variables = {
            "title": "Test Book",
        }

        result = render_nfo_template(template, variables)

        assert "Test Book" in result
        assert "{{author}}" not in result

    def test_render_conditional_if(self):
        """
        Test : Conditionnelles {{#if variable}}...{{/if}}.
        """
        template = "Title: {{title}}\n{{#if isbn}}ISBN: {{isbn}}{{/if}}"
        variables = {
            "title": "Test Book",
            "isbn": "1234567890",
        }

        result = render_nfo_template(template, variables)

        assert "ISBN: 1234567890" in result

    def test_render_conditional_if_empty(self):
        """
        Test : Conditionnelles avec variable vide excluent le contenu.
        """
        template = "Title: {{title}}\n{{#if isbn}}ISBN: {{isbn}}{{/if}}"
        variables = {
            "title": "Test Book",
            "isbn": "",
        }

        result = render_nfo_template(template, variables)

        assert "ISBN:" not in result

    def test_render_conditional_ifnot(self):
        """
        Test : Conditionnelles inverses {{#ifnot variable}}...{{/ifnot}}.
        """
        template = "Title: {{title}}\n{{#ifnot isbn}}No ISBN available{{/ifnot}}"
        variables = {
            "title": "Test Book",
            "isbn": None,
        }

        result = render_nfo_template(template, variables)

        assert "No ISBN available" in result

    def test_render_multiline_conditional(self):
        """
        Test : Conditionnelles multi-lignes.
        """
        template = """Title: {{title}}
{{#if url}}
URL: {{url}}
{{/if}}
Author: {{author}}"""
        variables = {
            "title": "Test Book",
            "url": "https://example.com",
            "author": "Test Author",
        }

        result = render_nfo_template(template, variables)

        assert "URL: https://example.com" in result

    def test_get_template_variables(self):
        """
        Test : Extraction des variables depuis un template.
        """
        template = "Title: {{title}}\nAuthor: {{author}}\nISBN: {{isbn}}"

        variables = get_template_variables(template)

        assert "title" in variables
        assert "author" in variables
        assert "isbn" in variables


class TestNfoTemplateModel:
    """Tests pour le modèle NfoTemplate."""

    def test_template_get_variables(self):
        """
        Test : Récupération variables depuis modèle.
        """
        template = NfoTemplate(
            name="test_template",
            content="Title: {{title}}",
            variables={"title": "Test Book"},
        )

        variables = template.get_variables()

        assert variables == {"title": "Test Book"}

    def test_template_set_variables(self):
        """
        Test : Définition variables dans modèle.
        """
        template = NfoTemplate(
            name="test_template",
            content="Title: {{title}}",
        )

        template.set_variables({"title": "Test Book", "author": "Test Author"})

        assert template.get_variables() == {
            "title": "Test Book",
            "author": "Test Author",
        }
