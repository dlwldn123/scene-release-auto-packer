"""
Tests d'intégration pour les services principaux.

Ces tests vérifient que les services fonctionnent ensemble correctement.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from web.app import create_app
from web.database import db
from web.models.destination import Destination
from web.models.job import Job, JobStatus
from web.models.user import User, UserRole
from web.services.ftp_upload import FtpUploadService
from web.services.packaging import PackagingService


@pytest.fixture
def app():
    """Créer une instance Flask pour les tests."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Créer un utilisateur de test."""
    with app.app_context():
        user = User(
            username="test_user",
            email="test@example.com",
            role=UserRole.OPERATOR,
        )
        user.set_password("test_password")
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def temp_dir():
    """Créer un répertoire temporaire pour les tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


class TestPackagingServiceIntegration:
    """Tests d'intégration pour PackagingService."""

    def test_pack_ebook_creates_job(self, app, test_user, temp_dir):
        """
        Test : Packaging eBook crée un job avec statut correct.
        """
        with app.app_context():
            # Créer un fichier eBook de test
            ebook_file = temp_dir / "test.epub"
            ebook_file.write_bytes(b"PK\x03\x04fake epub content")

            service = PackagingService(user_id=test_user.id)

            # Mock process_ebook pour éviter dépendances externes
            with patch("web.services.packaging.process_ebook") as mock_process:
                mock_process.return_value = "test.book.2023.epub-testgrp"

                job = service.pack_ebook(
                    ebook_path=ebook_file,
                    group="TESTGRP",
                    output_dir=temp_dir,
                )

                assert job is not None
                assert job.type == "EBOOK"
                assert job.group_name == "TESTGRP"
                # Le statut devrait être COMPLETED après packaging réussi
                # Note: Le mock simule un packaging réussi, donc le service devrait marquer comme COMPLETED
                assert job.status in [JobStatus.COMPLETED, JobStatus.RUNNING]
                assert job.user_id == test_user.id

    def test_pack_docs_creates_job(self, app, test_user, temp_dir):
        """
        Test : Packaging DOCS crée un job avec statut correct.
        """
        with app.app_context():
            # Créer un fichier PDF de test
            pdf_file = temp_dir / "test.pdf"
            pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

            service = PackagingService(user_id=test_user.id)

            # Mock pack_docs_release
            with patch("web.services.packaging.pack_docs_release") as mock_pack:
                mock_pack.return_value = "test.doc.2023.pdf-testgrp"

                job = service.pack_docs(
                    doc_path=pdf_file,
                    group="TESTGRP",
                    output_dir=temp_dir,
                )

                assert job is not None
                assert job.type == "DOCS"
                assert job.group_name == "TESTGRP"
                # Le statut devrait être COMPLETED après packaging réussi
                assert job.status in [JobStatus.COMPLETED, JobStatus.RUNNING]

    def test_pack_tv_creates_job(self, app, test_user, temp_dir):
        """
        Test : Packaging TV crée un job avec statut correct.
        """
        with app.app_context():
            # Créer un fichier vidéo de test
            mkv_file = temp_dir / "test.mkv"
            mkv_file.write_bytes(b"fake mkv content")

            service = PackagingService(user_id=test_user.id)

            # Mock pack_tv_release
            with patch("web.services.packaging.pack_tv_release") as mock_pack:
                mock_pack.return_value = temp_dir / "release_name"

                job = service.pack_tv(
                    input_mkv=mkv_file,
                    release_name="Test.Series.S01E01.720p.HDTV.x264-TESTGRP",
                    output_dir=temp_dir,
                )

                assert job is not None
                assert job.type == "TV"
                # Le statut devrait être COMPLETED après packaging réussi
                assert job.status in [JobStatus.COMPLETED, JobStatus.RUNNING]


class TestFtpUploadServiceIntegration:
    """Tests d'intégration pour FtpUploadService."""

    def test_upload_service_logs_to_job(self, app, test_user):
        """
        Test : Upload service log dans job_logs.
        """
        with app.app_context():
            # Créer un job
            job = Job(
                job_id="test-job-123",
                user_id=test_user.id,
                status=JobStatus.COMPLETED,
                type="EBOOK",
                group_name="TESTGRP",
            )
            db.session.add(job)
            db.session.commit()

            # Créer destination FTP
            destination = Destination(
                name="test_ftp",
                type="ftp",
                host="ftp.example.com",
                port=21,
                username="test_user",
                path="/uploads",
                user_id=test_user.id,
            )
            destination.set_password("test_password")
            db.session.add(destination)
            db.session.commit()

            # Créer service avec job_id
            upload_service = FtpUploadService(job_id=job.id)

            # Mock FTP upload
            with patch("web.services.ftp_upload.ftplib.FTP") as mock_ftp:
                mock_ftp_instance = MagicMock()
                mock_ftp.return_value.__enter__.return_value = mock_ftp_instance

                # Simuler upload réussi
                test_file = Path("/tmp/test.zip")
                test_file.touch()

                success, message = upload_service.upload_to_ftp(
                    destination.id,
                    [test_file],
                )

                # Vérifier que des logs ont été ajoutés
                logs = Job.query.get(job.id).logs
                assert len(logs) > 0
                assert any("INFO" in log.level for log in logs)

                test_file.unlink()


class TestServiceErrors:
    """Tests de gestion d'erreurs dans les services."""

    def test_packaging_service_handles_missing_file(self, app, test_user):
        """
        Test : PackagingService gère fichier introuvable.
        """
        with app.app_context():
            service = PackagingService(user_id=test_user.id)

            with pytest.raises(FileNotFoundError):
                service.pack_ebook(
                    ebook_path=Path("/nonexistent/file.epub"),
                    group="TESTGRP",
                )

    def test_packaging_service_handles_invalid_user(self, app):
        """
        Test : PackagingService gère utilisateur invalide.
        """
        with app.app_context():
            with pytest.raises(ValueError, match="Utilisateur.*introuvable"):
                PackagingService(user_id=99999)

    def test_ftp_upload_handles_invalid_destination(self, app):
        """
        Test : FtpUploadService gère destination invalide.
        """
        with app.app_context():
            service = FtpUploadService()

            success, message = service.upload_to_ftp(99999, [])

            assert success is False
            assert "introuvable" in message.lower()
