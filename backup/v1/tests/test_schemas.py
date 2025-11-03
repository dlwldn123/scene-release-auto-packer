"""
Tests unitaires pour schémas Marshmallow.
"""

import pytest
from marshmallow import ValidationError as MarshmallowValidationError

from web.schemas import ExtractMetadataIn, GroupUpdateIn, PackEbookIn, PackTvIn


def test_pack_ebook_in_valid():
    """Test validation schéma PackEbookIn valide."""
    schema = PackEbookIn()
    data = {
        "file_path": "/path/to/book.epub",
        "group": "TESTGRP",
        "source": "RETAIL",
        "enable_api": True,
    }
    result = schema.load(data)
    assert result["file_path"] == "/path/to/book.epub"
    assert result["group"] == "TESTGRP"


def test_pack_ebook_in_invalid_group():
    """Test validation schéma PackEbookIn avec groupe invalide."""
    schema = PackEbookIn()
    data = {
        "file_path": "/path/to/book.epub",
        "group": "A",  # Trop court
    }
    with pytest.raises(MarshmallowValidationError):
        schema.load(data)


def test_pack_ebook_in_missing_fields():
    """Test validation schéma PackEbookIn avec champs manquants."""
    schema = PackEbookIn()
    data = {
        "file_path": "/path/to/book.epub",
        # group manquant
    }
    with pytest.raises(MarshmallowValidationError):
        schema.load(data)


def test_pack_tv_in_valid():
    """Test validation schéma PackTvIn valide."""
    schema = PackTvIn()
    data = {
        "file_path": "/path/to/video.mkv",
        "release": "Test.Release.2023.1080p.HDTV.x264-TESTGRP",
        "link": "https://example.com",
    }
    result = schema.load(data)
    assert result["file_path"] == "/path/to/video.mkv"
    assert result["release"] == "Test.Release.2023.1080p.HDTV.x264-TESTGRP"


def test_extract_metadata_in_valid():
    """Test validation schéma ExtractMetadataIn valide."""
    schema = ExtractMetadataIn()
    data = {
        "file_path": "/path/to/book.epub",
        "enable_api": False,
    }
    result = schema.load(data)
    assert result["file_path"] == "/path/to/book.epub"
    assert result["enable_api"] is False


def test_group_update_in_valid():
    """Test validation schéma GroupUpdateIn valide."""
    schema = GroupUpdateIn()
    data = {"group": "TESTGRP"}
    result = schema.load(data)
    assert result["group"] == "TESTGRP"
