"""
Tests validation releases.
"""

from pathlib import Path

import pytest

from src.utils.validator import _validate_naming, validate_release


def test_validate_release_complete(temp_release_dir):
    """Test validation release complète."""
    # Créer fichiers minimaux
    (temp_release_dir / "release.nfo").write_text("Test NFO")
    (temp_release_dir / "release.sfv").write_text("test.rar ABCDEF01")
    (temp_release_dir / "FILE_ID.DIZ").write_text("Test Release")
    (temp_release_dir / "release.ZIP").write_bytes(b"PK\x03\x04")

    sample_dir = temp_release_dir / "Sample"
    sample_dir.mkdir()
    (sample_dir / "sample.pdf").write_bytes(b"%PDF")

    is_valid, errors = validate_release(
        temp_release_dir,
        "test.release.2023.retail.epub-english.testgrp",
        config={"check_naming": False},  # Désactiver validation nommage pour simplicité
    )

    # Devrait être valide avec fichiers présents
    assert is_valid is True or len(errors) == 0


def test_validate_release_missing_nfo(temp_release_dir):
    """Test erreur si NFO manquant."""
    # Créer fichiers sauf NFO
    (temp_release_dir / "release.sfv").write_text("test.rar ABCDEF01")

    is_valid, errors = validate_release(
        temp_release_dir,
        "test",
        config={"check_nfo": True},
    )

    assert is_valid is False
    assert any("NFO" in error for error in errors)


def test_validate_naming():
    """Test validation format nom release."""
    # Nom valide
    assert _validate_naming("author.title.2023.retail.epub-english.group") is True

    # Nom invalide (trop court)
    assert _validate_naming("short") is False

    # Nom invalide (pas de format-lang)
    assert _validate_naming("author.title.year") is False
