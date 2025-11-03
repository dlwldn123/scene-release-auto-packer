"""
Tests unitaires pour extraction de métadonnées.
"""

from pathlib import Path

import pytest

from src.metadata import detect_format, extract_epub_metadata


def test_detect_format_epub(sample_epub):
    """Test détection format EPUB."""
    format_type = detect_format(sample_epub)
    assert format_type == "epub"


def test_detect_format_pdf(sample_pdf):
    """Test détection format PDF."""
    format_type = detect_format(sample_pdf)
    assert format_type == "pdf"


def test_extract_epub_metadata(sample_epub):
    """Test extraction métadonnées EPUB."""
    metadata = extract_epub_metadata(sample_epub)
    assert isinstance(metadata, dict)
    assert "title" in metadata
    assert "author" in metadata
    assert "format" in metadata
    assert metadata["format"] == "EPUB"


def test_extract_epub_metadata_nonexistent():
    """Test extraction métadonnées fichier inexistant."""
    from src.metadata.epub import extract_epub_metadata

    metadata = extract_epub_metadata(Path("/nonexistent/file.epub"))
    assert metadata["title"] is None or metadata["title"] == "Unknown"
    assert metadata["format"] == "EPUB"
