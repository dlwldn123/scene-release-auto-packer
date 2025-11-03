"""
Tests unitaires pour génération de noms de releases.
"""

import pytest

from src.utils.naming import generate_release_name, normalize_string


def test_generate_release_name():
    """Test génération nom release."""
    metadata = {
        "title": "Test Book",
        "author": "Test Author",
        "year": "2023",
        "language": "en",
    }
    release_name = generate_release_name(metadata, "EPUB", "TESTGRP")
    assert "test" in release_name.lower()
    assert "epub" in release_name.lower()
    assert "testgrp" in release_name.lower()
    assert "2023" in release_name


def test_generate_release_name_retail():
    """Test génération nom release avec source RETAIL."""
    metadata = {
        "title": "Test Book",
        "author": "Test Author",
        "year": "2023",
        "language": "en",
    }
    release_name = generate_release_name(
        metadata, "EPUB", "TESTGRP", source_type="RETAIL"
    )
    assert "retail" in release_name.lower()


def test_normalize_string():
    """Test normalisation string."""
    assert normalize_string("Test Book") == "test.book"
    assert normalize_string("Test-Book") == "test-book"
    assert normalize_string("Test  Book") == "test.book"
    assert normalize_string("") == "Unknown"


def test_normalize_string_accent():
    """Test normalisation avec accents."""
    assert normalize_string("Café") == "cafe"
    assert normalize_string("Éléphant") == "elephant"


def test_generate_release_name_invalid_group():
    """Test génération nom release avec groupe invalide."""
    metadata = {"title": "Test", "author": "Author", "year": "2023"}
    with pytest.raises(ValueError):
        generate_release_name(metadata, "EPUB", "A")  # Trop court
