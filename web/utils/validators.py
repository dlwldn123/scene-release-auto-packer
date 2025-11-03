"""Validation utilities."""

from __future__ import annotations

import re


def validate_scene_group(group: str) -> bool:
    """Validate Scene group name format.

    Args:
        group: Group name to validate.

    Returns:
        True if valid Scene group format.
    """
    if not group or len(group) < 2 or len(group) > 30:
        return False

    # Scene group format: alphanumeric and hyphen, no spaces
    pattern = r"^[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]$"
    return bool(re.match(pattern, group))


def validate_release_type(release_type: str) -> bool:
    """Validate release type.

    Args:
        release_type: Release type to validate.

    Returns:
        True if valid release type.
    """
    valid_types = ["EBOOK", "TV", "DOCS", "AUDIOBOOK", "GAME"]
    return release_type.upper() in valid_types
