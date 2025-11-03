"""
Tests unitaires pour les exceptions personnalisées.
"""

import pytest

from src.exceptions import (
    APIError,
    ApplicationError,
    ConfigurationError,
    FileNotFoundError,
    MetadataError,
    PackagingError,
    ValidationError,
)


def test_application_error():
    """Test ApplicationError de base."""
    error = ApplicationError("Test error", error_type="TestError", status_code=500)
    assert error.message == "Test error"
    assert error.error_type == "TestError"
    assert error.status_code == 500
    assert error.field is None
    assert error.value is None

    error_dict = error.to_dict()
    assert error_dict["success"] is False
    assert error_dict["error"] == "Test error"
    assert error_dict["error_type"] == "TestError"


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Invalid field", field="test_field", value="bad_value")
    assert error.message == "Invalid field"
    assert error.error_type == "ValidationError"
    assert error.status_code == 400
    assert error.field == "test_field"
    assert error.value == "bad_value"

    error_dict = error.to_dict()
    assert error_dict["field"] == "test_field"
    assert error_dict["value"] == "bad_value"


def test_file_not_found_error():
    """Test FileNotFoundError."""
    error = FileNotFoundError("/path/to/file")
    assert "file" in error.message.lower()
    assert error.field == "file_path"
    assert error.value == "/path/to/file"
    assert error.status_code == 404


def test_packaging_error():
    """Test PackagingError."""
    error = PackagingError("Packaging failed", details="RAR CLI not found")
    assert error.message == "Packaging failed"
    assert error.details == "RAR CLI not found"

    error_dict = error.to_dict()
    assert error_dict["details"] == "RAR CLI not found"


def test_metadata_error():
    """Test MetadataError."""
    error = MetadataError("Metadata extraction failed", format_type="EPUB")
    assert error.message == "Metadata extraction failed"
    assert error.format_type == "EPUB"

    error_dict = error.to_dict()
    assert error_dict["format_type"] == "EPUB"


def test_api_error():
    """Test APIError."""
    error = APIError("API call failed", provider="GoogleBooks")
    assert error.message == "API call failed"
    assert error.provider == "GoogleBooks"
    assert error.status_code == 502

    error_dict = error.to_dict()
    assert error_dict["provider"] == "GoogleBooks"


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Config file not found")
    assert error.message == "Config file not found"
    assert error.error_type == "ConfigurationError"
    assert error.status_code == 500
