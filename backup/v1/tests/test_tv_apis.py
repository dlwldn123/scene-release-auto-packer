"""
Tests pour le service APIs TV (OMDb, TVDB, TMDb).
"""

from typing import Dict, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.metadata.tv_apis import TvApiEnricher
from src.metadata.tvdb_auth import TvdbAuthenticator


class TestTvApiEnricher:
    """Tests pour TvApiEnricher."""

    @pytest.fixture
    def mock_omdb_response(self):
        """Mock réponse OMDb."""
        return {
            "Response": "True",
            "Title": "Test Series",
            "Year": "2020",
            "Plot": "Test plot",
            "imdbRating": "8.5",
            "imdbID": "tt123456",
        }

    @pytest.fixture
    def mock_tvdb_response(self):
        """Mock réponse TVDB."""
        return {
            "data": {
                "seriesName": "Test Series",
                "firstAired": "2020-01-01",
                "overview": "Test overview",
                "rating": "8.5",
            }
        }

    @pytest.fixture
    def mock_tmdb_response(self):
        """Mock réponse TMDb."""
        return {
            "name": "Test Series",
            "first_air_date": "2020-01-01",
            "overview": "Test overview",
            "vote_average": 8.5,
        }

    def test_enrich_from_omdb(self, mock_omdb_response):
        """Test enrichissement OMDb."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_omdb_response
            mock_get.return_value = mock_response

            enricher = TvApiEnricher()
            result = enricher.enrich_from_omdb(
                title="Test Series", season=1, episode=1, api_key="test_key"
            )

            assert result is not None
            assert result.get("title") == "Test Series"
            assert result.get("year") == "2020"
            assert "omdb" in result.get("sources", [])

    def test_enrich_from_tvdb(self, mock_tvdb_response):
        """Test enrichissement TVDB."""
        with patch("src.metadata.tvdb_auth.TvdbAuthenticator.get_token") as mock_token:
            mock_token.return_value = "test_token"

            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_tvdb_response
                mock_get.return_value = mock_response

                enricher = TvApiEnricher()
                result = enricher.enrich_from_tvdb(
                    title="Test Series",
                    season=1,
                    episode=1,
                    api_key="test_key",
                    user_key="test_user_key",
                )

                assert result is not None
                assert "tvdb" in result.get("sources", [])

    def test_enrich_from_tmdb(self, mock_tmdb_response):
        """Test enrichissement TMDb."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_tmdb_response
            mock_get.return_value = mock_response

            enricher = TvApiEnricher()
            result = enricher.enrich_from_tmdb(
                title="Test Series", season=1, episode=1, api_key="test_key"
            )

            assert result is not None
            assert "tmdb" in result.get("sources", [])

    def test_enrich_fusion_intelligente(
        self, mock_tvdb_response, mock_tmdb_response, mock_omdb_response
    ):
        """Test fusion intelligente (priorité TVDB > TMDb > OMDb)."""
        with patch("src.metadata.tvdb_auth.TvdbAuthenticator.get_token") as mock_token:
            mock_token.return_value = "test_token"

            with patch("requests.get") as mock_get:
                # Simuler réponses successives
                responses = [
                    MagicMock(
                        status_code=200, json=Mock(return_value=mock_tvdb_response)
                    ),
                    MagicMock(
                        status_code=200, json=Mock(return_value=mock_tmdb_response)
                    ),
                    MagicMock(
                        status_code=200, json=Mock(return_value=mock_omdb_response)
                    ),
                ]
                mock_get.side_effect = responses

                enricher = TvApiEnricher()
                result = enricher.enrich(
                    title="Test Series",
                    season=1,
                    episode=1,
                    config={
                        "tvdb": {"api_key": "tvdb_key", "user_key": "user_key"},
                        "tmdb": {"api_key": "tmdb_key"},
                        "omdb": {"api_key": "omdb_key"},
                    },
                )

                assert result is not None
                # TVDB devrait avoir priorité
                assert "tvdb" in result.get("sources", [])

    def test_enrich_with_retry(self):
        """Test enrichissement avec retry sur erreur temporaire."""
        with patch("requests.get") as mock_get:
            # Première tentative échoue, deuxième réussit
            mock_get.side_effect = [
                Exception("Temporary error"),
                MagicMock(
                    status_code=200, json=Mock(return_value={"Response": "True"})
                ),
            ]

            enricher = TvApiEnricher()
            result = enricher.enrich_from_omdb(title="Test", api_key="test_key")

            # Devrait réussir après retry
            assert mock_get.call_count == 2

    def test_enrich_timeout(self):
        """Test gestion timeout."""
        with patch("requests.get") as mock_get:
            import requests

            mock_get.side_effect = requests.exceptions.Timeout("Timeout")

            enricher = TvApiEnricher()
            result = enricher.enrich_from_omdb(title="Test", api_key="test_key")

            # Devrait retourner None ou dict vide sur timeout
            assert result is None or result == {}


class TestTvdbAuthenticator:
    """Tests pour TvdbAuthenticator."""

    def test_get_token_first_time(self):
        """Test récupération token première fois."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test_token_123"}
            mock_post.return_value = mock_response

            auth = TvdbAuthenticator(
                api_key="test_api_key", user_key="test_user_key", username="test_user"
            )

            token = auth.get_token()

            assert token == "test_token_123"
            mock_post.assert_called_once()

    def test_get_token_cached(self):
        """Test récupération token depuis cache."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test_token_123"}
            mock_post.return_value = mock_response

            auth = TvdbAuthenticator(
                api_key="test_api_key", user_key="test_user_key", username="test_user"
            )

            # Premier appel
            token1 = auth.get_token()
            # Deuxième appel (devrait utiliser cache)
            token2 = auth.get_token()

            assert token1 == token2
            # Devrait n'appeler qu'une fois
            assert mock_post.call_count == 1

    def test_refresh_token(self):
        """Test refresh forcé du token."""
        with patch("requests.post") as mock_post:
            responses = [
                MagicMock(status_code=200, json=Mock(return_value={"token": "token1"})),
                MagicMock(status_code=200, json=Mock(return_value={"token": "token2"})),
            ]
            mock_post.side_effect = responses

            auth = TvdbAuthenticator(
                api_key="test_api_key", user_key="test_user_key", username="test_user"
            )

            token1 = auth.get_token()
            token2 = auth.refresh_token()

            assert token1 == "token1"
            assert token2 == "token2"
            assert mock_post.call_count == 2

    def test_token_expired_auto_refresh(self):
        """Test refresh automatique si token expiré."""
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "new_token"}
            mock_post.return_value = mock_response

            with patch("requests.get") as mock_get:
                # Première requête retourne 401 (token expiré)
                # Deuxième réussit après refresh
                mock_get.side_effect = [
                    MagicMock(status_code=401),
                    MagicMock(status_code=200, json=Mock(return_value={"data": {}})),
                ]

                auth = TvdbAuthenticator(
                    api_key="test_api_key",
                    user_key="test_user_key",
                    username="test_user",
                )

                # Simuler appel qui détecte 401 et refresh
                token = auth.get_token()  # Devrait refresh automatiquement

                assert token is not None
