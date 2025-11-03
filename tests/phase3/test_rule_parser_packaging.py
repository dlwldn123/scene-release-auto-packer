"""Tests for packaging rules extraction (Phase 3)."""

from __future__ import annotations

from web.services.rule_parser import RuleParserService


def test_extract_packaging_rules_with_zip_sizes() -> None:
    """Test extraction packaging rules with ZIP sizes."""
    parser = RuleParserService()

    rule_content = """
    PACKAGING
    ZIP sizes: 5MB, 10MB, 50MB, 100MB, 150MB, 200MB, 250MB
    ZIP+DIZ obligatoire
    """

    packaging_rules = parser.extract_packaging_rules(rule_content)

    assert packaging_rules is not None
    assert "zip" in packaging_rules
    assert len(packaging_rules["zip"]["allowed_sizes"]) > 0


def test_extract_packaging_rules_default() -> None:
    """Test extraction packaging rules with defaults."""
    parser = RuleParserService()

    packaging_rules = parser.extract_packaging_rules("")

    assert packaging_rules is not None
    assert "zip" in packaging_rules
    assert "rar" in packaging_rules
    assert "nfo" in packaging_rules
    assert "diz" in packaging_rules
    assert packaging_rules["zip"]["required"] is True
    assert packaging_rules["nfo"]["required"] is True
    assert packaging_rules["diz"]["required"] is True
    assert packaging_rules["rar"]["required"] is False
