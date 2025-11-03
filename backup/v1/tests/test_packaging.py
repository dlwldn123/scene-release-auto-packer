"""
Tests packaging et génération fichiers release.
"""

from pathlib import Path

import pytest

from src.packaging import generate_diz, generate_nfo, generate_sfv


def test_generate_nfo_ascii(temp_release_dir):
    """Test génération NFO avec encodage ASCII."""
    metadata = {
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "year": "2023",
        "language": "en",
        "isbn": None,
        "format": "EPUB",
    }

    nfo_path = generate_nfo(
        "test.release.2023.retail.epub-english.testgrp",
        metadata,
        "TESTGRP",
        release_dir=temp_release_dir,
        max_width=80,
    )

    assert nfo_path.exists()

    # Vérifier largeur lignes ≤80
    content = nfo_path.read_bytes()
    # Décoder pour vérifier
    try:
        text = content.decode("utf-8")
    except (UnicodeDecodeError, ValueError) as e:
        logger.debug(f"Erreur décodage UTF-8: {e}, fallback windows-1252")
        text = content.decode("windows-1252", errors="ignore")

    for line in text.splitlines():
        assert len(line) <= 80


def test_generate_sfv_crc32(temp_release_dir):
    """Test génération SFV avec CRC32."""
    # Créer fichier test
    test_file = temp_release_dir / "test.txt"
    test_file.write_text("test content")

    sfv_path = generate_sfv(
        "test.release",
        temp_release_dir,
        files_to_verify=[test_file],
    )

    assert sfv_path.exists()

    content = sfv_path.read_text()
    assert "test.txt" in content
    # Vérifier format CRC32 (8 hex digits)
    import re

    assert re.search(r"\b[0-9A-Fa-f]{8}\b", content)


def test_generate_diz_format(temp_release_dir):
    """Test génération DIZ conforme."""
    diz_path = generate_diz(
        "test.release",
        temp_release_dir,
        num_disks=2,
        max_width=44,
        max_lines=30,
    )

    assert diz_path.exists()

    content = diz_path.read_text()
    lines = content.splitlines()

    # Vérifier largeur ≤44
    for line in lines:
        assert len(line) <= 44

    # Vérifier lignes ≤30
    assert len(lines) <= 30
