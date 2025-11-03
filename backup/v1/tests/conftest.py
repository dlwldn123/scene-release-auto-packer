"""
Fixtures et configuration pour tests pytest.
"""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Crée un dossier temporaire pour les tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_release_dir(temp_dir):
    """Crée un dossier release temporaire pour les tests."""
    release_dir = temp_dir / "test_release"
    release_dir.mkdir(parents=True, exist_ok=True)
    return release_dir


@pytest.fixture
def sample_epub(temp_dir):
    """Crée un fichier EPUB de test minimal."""
    epub_path = temp_dir / "test.epub"
    # Créer un ZIP minimal (EPUB est un ZIP)
    import zipfile

    with zipfile.ZipFile(epub_path, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
        )
        zf.writestr(
            "content.opf",
            """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:language>en</dc:language>
    <dc:date>2023-01-01</dc:date>
  </metadata>
</package>""",
        )
    return epub_path


@pytest.fixture
def sample_pdf(temp_dir):
    """Crée un fichier PDF de test minimal."""
    pdf_path = temp_dir / "test.pdf"
    # PDF minimal (header seulement)
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture
def sample_config():
    """Retourne une configuration de test."""
    return {
        "api": {
            "enable_googlebooks": False,
            "enable_openlibrary": False,
            "rate_limit_delay": 0.1,
            "timeout": 5,
        },
        "nfo": {
            "ascii_art": False,
            "max_width": 80,
            "template_path": "templates/nfo_template.txt",
        },
        "rar": {
            "create_for_zip": True,
            "method": 5,
        },
        "zip": {
            "allowed_sizes": [5000000, 10000000],
            "use_83_rule": True,
        },
        "validation": {
            "check_naming": False,  # Désactiver pour tests
            "check_nfo": True,
            "check_rar": False,
            "check_sample": True,
            "check_sfv": True,
        },
        "sample": {
            "pdf": {"amount": 2, "type": "pages"},
            "epub": {"amount": 1, "type": "chapter"},
        },
    }
