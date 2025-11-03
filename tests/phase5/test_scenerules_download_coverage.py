"""Additional tests for ScenerulesDownloadService to achieve ≥90% coverage."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from web.services.scenerules_download import ScenerulesDownloadService


def test_download_rule_unicode_decode_error() -> None:
    """Test download_rule with UnicodeDecodeError fallback to ISO-8859-1."""
    service = ScenerulesDownloadService()
    
    # Mock response with UnicodeDecodeError on text, fallback to ISO-8859-1
    mock_response = Mock()
    mock_response.content = b"\xc9\xe0\xe8\xf9"  # ISO-8859-1 bytes
    mock_response.raise_for_status = Mock()
    
    # Create a property that raises UnicodeDecodeError when accessed
    class TextProperty:
        def __get__(self, obj, objtype=None):
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
    
    type(mock_response).text = TextProperty()
    
    with patch.object(service.session, "get", return_value=mock_response):
        result = service.download_rule("eBOOK", 2022)
        assert result["content"] == "\xc9\xe0\xe8\xf9"  # Decoded ISO-8859-1


def test_download_rule_scene_not_english() -> None:
    """Test download_rule with scene != English."""
    service = ScenerulesDownloadService()
    
    mock_response = Mock()
    mock_response.text = "Test content"
    mock_response.raise_for_status = Mock()
    
    with patch.object(service.session, "get", return_value=mock_response):
        result = service.download_rule("eBOOK", 2022, scene="French")
        assert "[French]" in result["name"]


def test_download_rule_http_error_404() -> None:
    """Test download_rule with HTTP 404 error."""
    service = ScenerulesDownloadService()
    
    mock_response = Mock()
    mock_response.status_code = 404
    mock_http_error = requests.exceptions.HTTPError(response=mock_response)
    mock_response.raise_for_status = Mock(side_effect=mock_http_error)
    
    with patch.object(service.session, "get", return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            service.download_rule("NONEXISTENT", 2022)
        assert "Rule not found" in str(exc_info.value)


def test_download_rule_http_error_other() -> None:
    """Test download_rule with HTTP error other than 404."""
    service = ScenerulesDownloadService()
    
    mock_response = Mock()
    mock_response.status_code = 500
    mock_http_error = requests.exceptions.HTTPError(response=mock_response)
    mock_response.raise_for_status = Mock(side_effect=mock_http_error)
    
    with patch.object(service.session, "get", return_value=mock_response):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            service.download_rule("eBOOK", 2022)
        assert "Failed to download rule" in str(exc_info.value)


def test_download_rule_request_exception() -> None:
    """Test download_rule with RequestException."""
    service = ScenerulesDownloadService()
    
    mock_exception = requests.exceptions.RequestException("Network error")
    
    with patch.object(service.session, "get", side_effect=mock_exception):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            service.download_rule("eBOOK", 2022)
        assert "Network error downloading rule" in str(exc_info.value)


def test_download_rule_by_url_unicode_decode_error() -> None:
    """Test download_rule_by_url with UnicodeDecodeError fallback."""
    service = ScenerulesDownloadService()
    
    mock_response = Mock()
    mock_response.content = b"\xc9\xe0\xe8\xf9"  # ISO-8859-1 bytes
    mock_response.raise_for_status = Mock()
    
    # Create a property that raises UnicodeDecodeError when accessed
    class TextProperty:
        def __get__(self, obj, objtype=None):
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
    
    type(mock_response).text = TextProperty()
    
    with patch.object(service.session, "get", return_value=mock_response):
        result = service.download_rule_by_url("https://scenerules.org/nfo/2022_eBOOK.nfo")
        assert result["content"] == "\xc9\xe0\xe8\xf9"  # Decoded ISO-8859-1


def test_download_rule_by_url_no_match() -> None:
    """Test download_rule_by_url with URL that doesn't match pattern."""
    service = ScenerulesDownloadService()
    
    mock_response = Mock()
    mock_response.text = "Test content"
    mock_response.raise_for_status = Mock()
    
    with patch.object(service.session, "get", return_value=mock_response):
        result = service.download_rule_by_url("https://scenerules.org/nfo/invalid.nfo")
        assert result["year"] == 2022
        assert result["section"] == "Unknown"


def test_download_rule_by_url_request_exception() -> None:
    """Test download_rule_by_url with RequestException."""
    service = ScenerulesDownloadService()
    
    mock_exception = requests.exceptions.RequestException("Network error")
    
    with patch.object(service.session, "get", side_effect=mock_exception):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            service.download_rule_by_url("https://scenerules.org/nfo/2022_eBOOK.nfo")
        assert "Failed to download rule from URL" in str(exc_info.value)
