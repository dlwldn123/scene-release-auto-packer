"""Additional tests for RuleParserService (Phase 3)."""

from __future__ import annotations

from web.services.rule_parser import RuleParserService


def test_extract_file_formats_default() -> None:
    """Test extraction formats avec contenu vide (defaults)."""
    parser = RuleParserService()

    formats = parser.extract_file_formats("")

    # Should return default formats from [2022] eBOOK rule
    assert ".pdf" in formats
    assert ".epub" in formats
    assert ".cbz" in formats


def test_extract_naming_format_default() -> None:
    """Test extraction format nommage avec contenu vide (defaults)."""
    parser = RuleParserService()

    naming_format = parser.extract_naming_format("")

    assert naming_format is not None
    assert "format" in naming_format
    assert "components" in naming_format
    assert (
        naming_format["format"]
        == "GroupName-Author-Title-Format-Language-Year-ISBN-eBook"
    )


def test_extract_required_files_default() -> None:
    """Test extraction fichiers requis avec contenu vide (defaults)."""
    parser = RuleParserService()

    required_files = parser.extract_required_files("")

    # Default based on [2022] eBOOK: ZIP+DIZ+NFO obligatoire
    assert "zip" in required_files
    assert "diz" in required_files
    assert "nfo" in required_files


def test_extract_packaging_rules() -> None:
    """Test extraction règles packaging."""
    parser = RuleParserService()

    packaging_rules = parser.extract_packaging_rules("")

    assert packaging_rules is not None
    assert "zip" in packaging_rules
    assert "rar" in packaging_rules
    assert "nfo" in packaging_rules
    assert "diz" in packaging_rules
    assert packaging_rules["zip"]["required"] is True
    assert len(packaging_rules["zip"]["allowed_sizes"]) > 0


def test_parse_ebook_rule_2022_complete_structure() -> None:
    """Test parsing complet avec structure valide."""
    parser = RuleParserService()

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
    assert isinstance(rule_spec, dict)
    assert "file_formats" in rule_spec
    assert "naming" in rule_spec
    assert "required_files" in rule_spec
    assert "packaging" in rule_spec

    # Verify file formats
    assert len(rule_spec["file_formats"]) > 0
    assert ".pdf" in rule_spec["file_formats"]

    # Verify naming format
    assert rule_spec["naming"]["format"] is not None

    # Verify required files
    assert len(rule_spec["required_files"]) > 0

    # Verify packaging rules
    assert rule_spec["packaging"]["zip"]["required"] is True
