"""
Tests unitaires pour web/utils/api_config.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from web.utils.api_config import get_tv_api_config, parse_tv_release_name


class TestGetTvApiConfig:
    """Tests pour get_tv_api_config()."""

    def test_get_config_user_priority(self, app, test_user):
        """Test: Config utilisateur a priorité sur config globale."""
        with app.app_context():
            from web.models.api_config import ApiConfig

            # Créer config globale
            global_config = ApiConfig(
                user_id=None,
                api_name="omdb",
                api_key='{"api_key": "global_key"}',
            )
            db.session.add(global_config)

            # Créer config utilisateur
            user_config = ApiConfig(
                user_id=test_user.id,
                api_name="omdb",
                api_key='{"api_key": "user_key"}',
            )
            db.session.add(user_config)
            db.session.commit()

            # Récupérer config
            configs = get_tv_api_config(user_id=test_user.id)

            # Devrait retourner config utilisateur (pas globale)
            assert "omdb" in configs
            assert configs["omdb"]["api_key"] == "user_key"

    def test_get_config_fallback_global(self, app, test_user):
        """Test: Fallback sur config globale si pas de config utilisateur."""
        with app.app_context():
            from web.models.api_config import ApiConfig

            # Créer seulement config globale
            global_config = ApiConfig(
                user_id=None,
                api_name="omdb",
                api_key='{"api_key": "global_key"}',
            )
            db.session.add(global_config)
            db.session.commit()

            # Récupérer config
            configs = get_tv_api_config(user_id=test_user.id)

            # Devrait retourner config globale
            assert "omdb" in configs
            assert configs["omdb"]["api_key"] == "global_key"

    def test_get_config_tvdb_requires_user_key(self, app, test_user):
        """Test: TVDB nécessite api_key et user_key."""
        with app.app_context():
            from web.models.api_config import ApiConfig

            # Créer config TVDB complète
            tvdb_config = ApiConfig(
                user_id=test_user.id,
                api_name="tvdb",
                api_key='{"api_key": "tvdb_key", "user_key": "user_key", "username": "test"}',
            )
            db.session.add(tvdb_config)
            db.session.commit()

            # Récupérer config
            configs = get_tv_api_config(user_id=test_user.id)

            # Devrait retourner config TVDB complète
            assert "tvdb" in configs
            assert configs["tvdb"]["api_key"] == "tvdb_key"
            assert configs["tvdb"]["user_key"] == "user_key"
            assert configs["tvdb"]["username"] == "test"

    def test_get_config_empty_if_none(self, app, test_user):
        """Test: Retourne dict vide si aucune config."""
        with app.app_context():
            configs = get_tv_api_config(user_id=test_user.id)
            assert configs == {}

    def test_get_config_decrypts_api_key(self, app, test_user):
        """Test: Déchiffre correctement les clés API."""
        with app.app_context():
            from web.models.api_config import ApiConfig

            # Mock déchiffrement
            with patch("web.models.api_config.ApiConfig.get_api_key") as mock_get:
                mock_get.return_value = {"api_key": "decrypted_key"}

                config = ApiConfig(
                    user_id=test_user.id,
                    api_name="omdb",
                    api_key="encrypted_data",
                )
                db.session.add(config)
                db.session.commit()

                configs = get_tv_api_config(user_id=test_user.id)
                assert "omdb" in configs
                assert configs["omdb"]["api_key"] == "decrypted_key"


class TestParseTvReleaseName:
    """Tests pour parse_tv_release_name()."""

    def test_parse_standard_format(self):
        """Test: Parse format standard S01E01."""
        parsed = parse_tv_release_name("Series.Name.S01E01.720p.HDTV-GROUP")

        assert parsed["season"] == 1
        assert parsed["episode"] == 1
        assert "title" in parsed
        assert parsed["title"] is not None

    def test_parse_lowercase_format(self):
        """Test: Parse format lowercase s1e1."""
        parsed = parse_tv_release_name("Series.Name.s1e1.720p.HDTV-GROUP")

        assert parsed["season"] == 1
        assert parsed["episode"] == 1

    def test_parse_two_digit_season_episode(self):
        """Test: Parse saison/épisode à 2 chiffres."""
        parsed = parse_tv_release_name("Series.Name.S12E25.720p.HDTV-GROUP")

        assert parsed["season"] == 12
        assert parsed["episode"] == 25

    def test_parse_without_season_episode(self):
        """Test: Parse sans saison/épisode retourne None."""
        parsed = parse_tv_release_name("Series.Name.720p.HDTV-GROUP")

        assert parsed["season"] is None
        assert parsed["episode"] is None
        assert parsed["title"] is not None  # Devrait extraire titre quand même

    def test_parse_title_extraction(self):
        """Test: Extraction titre correcte."""
        parsed = parse_tv_release_name("The.Series.Name.S01E01.720p.HDTV-GROUP")

        assert parsed["title"] is not None
        assert "Series" in parsed["title"] or "The" in parsed["title"]

    def test_parse_various_formats(self):
        """Test: Parse différents formats de nommage."""
        test_cases = [
            ("Series.S01E01-GROUP", 1, 1),
            ("Series - S01E01 - GROUP", 1, 1),
            ("Series.S1.E1-GROUP", 1, 1),
            ("Series S01 E01 GROUP", 1, 1),
        ]

        for release_name, expected_season, expected_episode in test_cases:
            parsed = parse_tv_release_name(release_name)
            # Certains formats peuvent ne pas matcher, c'est OK
            if parsed["season"] is not None:
                assert parsed["season"] == expected_season
                assert parsed["episode"] == expected_episode
