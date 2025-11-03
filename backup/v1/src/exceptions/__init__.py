"""
Exceptions personnalisées pour Scene Ebook Packer.
"""

from .application_exceptions import (
    APIError,
    ApplicationError,
    ConfigurationError,
    FileNotFoundError,
    MetadataError,
    PackagingError,
    ValidationError,
)

__all__ = [
    "ApplicationError",
    "ValidationError",
    "FileNotFoundError",
    "ConfigurationError",
    "PackagingError",
    "MetadataError",
    "APIError",
]

# Alias pour éviter conflit avec built-in FileNotFoundError
AppFileNotFoundError = FileNotFoundError
