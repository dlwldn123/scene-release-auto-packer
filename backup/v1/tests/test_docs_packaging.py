"""
Tests unitaires pour le packaging DOCS (TDD - GREEN phase).
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.packaging.docs_packer import extract_docs_metadata, pack_docs_release


class TestDocsPackaging:
    """Tests pour le packaging DOCS."""

    def test_extract_metadata_pdf(self, tmp_path):
        """Test : Extraction métadonnées PDF."""
        # Créer un PDF mock simple
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")

        # Le test devrait fonctionner même si le PDF n'a pas de métadonnées
        metadata = extract_docs_metadata(pdf_path)

        assert isinstance(metadata, dict)
        assert "title" in metadata
        assert "author" in metadata
        assert "format" in metadata
        assert metadata["format"] == "PDF"

    def test_extract_metadata_docx(self, tmp_path):
        """Test : Extraction métadonnées DOCX."""
        # Créer un fichier DOCX mock (ou skippé si python-docx non disponible)
        try:
            from docx import Document
        except ImportError:
            pytest.skip("python-docx non disponible")

        docx_path = tmp_path / "test.docx"
        doc = Document()
        doc.core_properties.title = "Test Document"
        doc.core_properties.author = "Test Author"
        doc.save(str(docx_path))

        metadata = extract_docs_metadata(docx_path)

        assert isinstance(metadata, dict)
        assert metadata["title"] == "Test Document"
        assert metadata["author"] == "Test Author"
        assert metadata["format"] == "DOCX"

    def test_extract_metadata_txt(self, tmp_path):
        """Test : Extraction métadonnées TXT."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("Test Title\nContent line 1\nContent line 2")

        metadata = extract_docs_metadata(txt_path)

        assert isinstance(metadata, dict)
        assert metadata["title"] == "Test Title"
        assert metadata["format"] == "TXT"

    def test_extract_metadata_fallback_filename(self, tmp_path):
        """Test : Fallback sur nom fichier si pas de métadonnées."""
        txt_path = tmp_path / "MyDocument.txt"
        txt_path.write_text("Content without title")

        metadata = extract_docs_metadata(txt_path)

        assert metadata["title"] == "MyDocument"

    @patch("src.packaging.docs_packer.generate_release_name")
    @patch("src.packaging.docs_packer.package_2022_format")
    @patch("src.packaging.docs_packer.generate_nfo")
    @patch("src.packaging.docs_packer.generate_diz")
    @patch("src.packaging.docs_packer.generate_sfv")
    def test_pack_docs_release_pdf(
        self, mock_sfv, mock_diz, mock_nfo, mock_package, mock_release_name, tmp_path
    ):
        """Test : Packaging release PDF complète."""
        # Créer document PDF mock
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")

        # Mock les dépendances
        mock_release_name.return_value = "Test.Document.2024.PDF-GROUP"
        mock_package.return_value = ["test.zip"]

        # Config mock
        config = {
            "nfo": {"max_width": 80, "ascii_art": True},
            "diz": {"filename": "FILE_ID.DIZ", "max_lines": 30, "max_width": 44},
            "rar": {"create_for_zip": False},
        }

        # Exécuter
        release_name = pack_docs_release(
            doc_path=pdf_path,
            group="GROUP",
            output_dir=tmp_path / "releases",
            config=config,
        )

        assert release_name == "Test.Document.2024.PDF-GROUP"
        mock_release_name.assert_called_once()
        mock_package.assert_called_once()
        mock_nfo.assert_called_once()
        mock_diz.assert_called_once()
        mock_sfv.assert_called_once()

    def test_pack_docs_release_file_not_found(self, tmp_path):
        """Test : Erreur si fichier introuvable."""
        non_existent = tmp_path / "nonexistent.pdf"

        with pytest.raises(FileNotFoundError):
            pack_docs_release(
                doc_path=non_existent,
                group="GROUP",
                output_dir=tmp_path / "releases",
            )

    @patch("src.packaging.docs_packer.generate_release_name")
    @patch("src.packaging.docs_packer.package_2022_format")
    @patch("src.packaging.docs_packer.generate_nfo")
    @patch("src.packaging.docs_packer.generate_diz")
    @patch("src.packaging.docs_packer.generate_sfv")
    def test_pack_docs_release_with_url(
        self, mock_sfv, mock_diz, mock_nfo, mock_package, mock_release_name, tmp_path
    ):
        """Test : Packaging avec URL."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")

        mock_release_name.return_value = "Test.Document.2024.PDF-GROUP"
        mock_package.return_value = ["test.zip"]

        config = {
            "nfo": {"max_width": 80, "ascii_art": True},
            "diz": {"filename": "FILE_ID.DIZ", "max_lines": 30, "max_width": 44},
            "rar": {"create_for_zip": False},
        }

        release_name = pack_docs_release(
            doc_path=pdf_path,
            group="GROUP",
            output_dir=tmp_path / "releases",
            url="https://example.com/release",
            config=config,
        )

        # Vérifier que generate_nfo a été appelé avec l'URL
        mock_nfo.assert_called_once()
        call_args = mock_nfo.call_args
        assert call_args[1]["url"] == "https://example.com/release"
