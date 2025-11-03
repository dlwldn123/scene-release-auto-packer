"""
Module d'extraction de métadonnées depuis fichiers eBooks.
"""

from src.metadata.api_enricher import MetadataEnricher
from src.metadata.detector import detect_format
from src.metadata.epub import extract_epub_metadata
from src.metadata.mobi import extract_mobi_metadata
from src.metadata.pdf import extract_pdf_metadata

__all__ = [
    "detect_format",
    "extract_epub_metadata",
    "extract_mobi_metadata",
    "extract_pdf_metadata",
    "MetadataEnricher",
]
