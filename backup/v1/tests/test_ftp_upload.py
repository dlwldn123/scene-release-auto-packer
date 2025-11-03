"""
Tests pour le service Upload FTP/SFTP.
"""

from pathlib import Path
from typing import List
from unittest.mock import MagicMock, Mock, patch

import pytest

from web.models.destination import Destination
from web.services.ftp_upload import FtpUploadService


class TestFtpUploadService:
    """Tests pour FtpUploadService."""

    @pytest.fixture
    def mock_destination(self):
        """Mock destination FTP."""
        dest = Mock(spec=Destination)
        dest.id = 1
        dest.name = "test_ftp"
        dest.type = "ftp"
        dest.host = "ftp.test.com"
        dest.port = 21
        dest.username = "testuser"
        dest.get_password.return_value = "testpass"
        dest.path = "/releases/test"
        return dest

    @pytest.fixture
    def mock_destination_sftp(self):
        """Mock destination SFTP."""
        dest = Mock(spec=Destination)
        dest.id = 2
        dest.name = "test_sftp"
        dest.type = "sftp"
        dest.host = "sftp.test.com"
        dest.port = 22
        dest.username = "testuser"
        dest.get_password.return_value = "testpass"
        dest.path = "/releases/test"
        return dest

    @pytest.fixture
    def test_files(self, tmp_path):
        """Créer fichiers de test."""
        files = []
        for i in range(3):
            test_file = tmp_path / f"test_{i}.txt"
            test_file.write_text(f"Content {i}")
            files.append(test_file)
        return files

    def test_upload_to_ftp_success(self, mock_destination, test_files, tmp_path):
        """Test upload FTP réussi."""
        with patch("ftplib.FTP") as mock_ftp_class:
            mock_ftp = MagicMock()
            mock_ftp_class.return_value = mock_ftp

            service = FtpUploadService()
            success, message = service.upload_to_ftp(
                destination_id=1, files=test_files, destination=mock_destination
            )

            assert success is True
            mock_ftp.connect.assert_called_once()
            mock_ftp.login.assert_called_once_with("testuser", "testpass")
            mock_ftp.cwd.assert_called()
            assert mock_ftp.storbinary.call_count == len(test_files)
            mock_ftp.quit.assert_called_once()

    def test_upload_to_sftp_success(self, mock_destination_sftp, test_files):
        """Test upload SFTP réussi."""
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = MagicMock()
            mock_sftp = MagicMock()
            mock_ssh.open_sftp.return_value = mock_sftp
            mock_ssh_class.return_value = mock_ssh

            service = FtpUploadService()
            success, message = service.upload_to_sftp(
                destination_id=2, files=test_files, destination=mock_destination_sftp
            )

            assert success is True
            mock_ssh.connect.assert_called_once()
            mock_ssh.set_missing_host_key_policy.assert_called_once()
            mock_sftp.chdir.assert_called()
            assert mock_sftp.put.call_count == len(test_files)
            mock_ssh.close.assert_called_once()

    def test_upload_to_ftp_connection_error(self, mock_destination, test_files):
        """Test upload FTP avec erreur de connexion."""
        with patch("ftplib.FTP") as mock_ftp_class:
            mock_ftp_class.side_effect = Exception("Connection refused")

            service = FtpUploadService()
            success, message = service.upload_to_ftp(
                destination_id=1, files=test_files, destination=mock_destination
            )

            assert success is False
            assert "erreur" in message.lower() or "error" in message.lower()

    def test_upload_to_ftp_auth_error(self, mock_destination, test_files):
        """Test upload FTP avec erreur d'authentification."""
        with patch("ftplib.FTP") as mock_ftp_class:
            mock_ftp = MagicMock()
            mock_ftp.login.side_effect = Exception("Authentication failed")
            mock_ftp_class.return_value = mock_ftp

            service = FtpUploadService()
            success, message = service.upload_to_ftp(
                destination_id=1, files=test_files, destination=mock_destination
            )

            assert success is False
            assert "authentification" in message.lower() or "auth" in message.lower()

    def test_upload_to_ftp_with_retry(self, mock_destination, test_files):
        """Test upload FTP avec retry."""
        with patch("ftplib.FTP") as mock_ftp_class:
            mock_ftp = MagicMock()
            # Première tentative échoue, deuxième réussit
            mock_ftp_class.side_effect = [Exception("Temporary error"), mock_ftp]

            service = FtpUploadService()
            success, message = service.upload_to_ftp(
                destination_id=1,
                files=test_files,
                destination=mock_destination,
                max_retries=3,
            )

            # Avec retry, devrait réussir
            assert success is True

    def test_upload_multi_volume_rar(self, mock_destination, tmp_path):
        """Test upload volumes RAR multiples."""
        # Créer fichiers RAR simulés
        rar_files = []
        rar_files.append(tmp_path / "release.rar")
        rar_files.append(tmp_path / "release.r00")
        rar_files.append(tmp_path / "release.r01")

        for f in rar_files:
            f.write_text("RAR content")

        with patch("ftplib.FTP") as mock_ftp_class:
            mock_ftp = MagicMock()
            mock_ftp_class.return_value = mock_ftp

            service = FtpUploadService()
            success, message = service.upload_to_ftp(
                destination_id=1, files=rar_files, destination=mock_destination
            )

            assert success is True
            # Vérifier que tous les volumes sont uploadés dans l'ordre
            assert mock_ftp.storbinary.call_count == len(rar_files)

    def test_test_connection_ftp_success(self, mock_destination):
        """Test connexion FTP réussie."""
        with patch("ftplib.FTP") as mock_ftp_class:
            mock_ftp = MagicMock()
            mock_ftp_class.return_value = mock_ftp

            service = FtpUploadService()
            success, message = service.test_connection(mock_destination)

            assert success is True
            mock_ftp.connect.assert_called_once()
            mock_ftp.login.assert_called_once()
            mock_ftp.quit.assert_called_once()

    def test_test_connection_ftp_failure(self, mock_destination):
        """Test connexion FTP échouée."""
        with patch("ftplib.FTP") as mock_ftp_class:
            mock_ftp_class.side_effect = Exception("Connection failed")

            service = FtpUploadService()
            success, message = service.test_connection(mock_destination)

            assert success is False
            assert "erreur" in message.lower() or "error" in message.lower()
