"""Tests for RuleParserService (Phase 3 - Prerequisites)."""

from __future__ import annotations

from web.services.rule_parser import RuleParserService


def test_parse_ebook_rule_2022_extract_file_formats() -> None:
    """Test extraction formats fichiers depuis règle [2022] eBOOK."""
    parser = RuleParserService()

    # Mock rule content (simplified version of [2022] eBOOK rule)
    rule_content = """
    OTHER
    PDF, EPUB, CBZ, Kindle (.azw, .kf8), MOBIPOCKET (.prc, .mobi)
    """

    formats = parser.extract_file_formats(rule_content)

    assert ".pdf" in formats
    assert ".epub" in formats
    assert ".cbz" in formats
    assert ".azw" in formats
    assert ".kf8" in formats
    assert ".mobi" in formats
    assert ".prc" in formats


def test_parse_ebook_rule_2022_extract_naming_format() -> None:
    """Test extraction format nommage depuis règle [2022] eBOOK."""
    parser = RuleParserService()

    # Mock rule content
    rule_content = """
    DIRNAMING
    GroupName-Author-Title-Format-Language-Year-ISBN-eBook
    """

    naming_format = parser.extract_naming_format(rule_content)

    assert naming_format is not None
    assert "format" in naming_format
    assert "components" in naming_format


def test_parse_ebook_rule_2022_extract_required_files() -> None:
    """Test extraction fichiers requis depuis règle [2022] eBOOK."""
    parser = RuleParserService()

    # Mock rule content
    rule_content = """
    PACKAGING
    ZIP+DIZ obligatoire
    .nfo file obligatoire
    """

    required_files = parser.extract_required_files(rule_content)

    assert "zip" in required_files
    assert "diz" in required_files
    assert "nfo" in required_files


def test_parse_ebook_rule_2022_complete() -> None:
    """Test parsing complet règle [2022] eBOOK."""
    parser = RuleParserService()

    # Mock rule content (simplified)
    rule_content = """
    [2022] eBOOK

    OTHER
    PDF, EPUB, CBZ, Kindle (.azw, .kf8), MOBIPOCKET (.prc, .mobi)

    PACKAGING
    ZIP+DIZ obligatoire
    .nfo file obligatoire

    DIRNAMING
    GroupName-Author-Title-Format-Language-Year-ISBN-eBook
    """

    rule_spec = parser.parse_ebook_rule_2022(rule_content)

    assert rule_spec is not None
    assert "file_formats" in rule_spec
    assert "naming" in rule_spec
    assert "required_files" in rule_spec
    assert "packaging" in rule_spec
