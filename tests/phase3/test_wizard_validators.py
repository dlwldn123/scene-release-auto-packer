"""Tests for wizard validators."""

from __future__ import annotations

import pytest

from web.utils.validators import validate_release_type, validate_scene_group


def test_validate_scene_group_valid() -> None:
    """Test validating valid Scene group names."""
    assert validate_scene_group("TestGroup") is True
    assert validate_scene_group("Test-Group") is True
    assert validate_scene_group("ABC123") is True
    assert validate_scene_group("A") is False  # Too short
    assert validate_scene_group("A" * 31) is False  # Too long


def test_validate_scene_group_invalid() -> None:
    """Test validating invalid Scene group names."""
    assert validate_scene_group("Invalid Group") is False  # Spaces
    assert validate_scene_group("-Invalid") is False  # Starts with hyphen
    assert validate_scene_group("Invalid-") is False  # Ends with hyphen
    assert validate_scene_group("") is False  # Empty
    assert validate_scene_group("Invalid!") is False  # Special chars


def test_validate_release_type_valid() -> None:
    """Test validating valid release types."""
    assert validate_release_type("EBOOK") is True
    assert validate_release_type("TV") is True
    assert validate_release_type("DOCS") is True
    assert validate_release_type("ebook") is True  # Case insensitive
    assert validate_release_type("tv") is True


def test_validate_release_type_invalid() -> None:
    """Test validating invalid release types."""
    assert validate_release_type("INVALID") is False
    assert validate_release_type("") is False
    assert validate_release_type("MOVIE") is False
