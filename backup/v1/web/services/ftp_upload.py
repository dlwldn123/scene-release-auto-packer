"""
Service pour upload FTP/SFTP des releases.
"""

import logging
import time
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import ftplib
except ImportError:
    ftplib = None

try:
    import paramiko
except ImportError:
    paramiko = None

from web.database import db
from web.models.destination import Destination
from web.models.job import Job, JobLog

logger = logging.getLogger(__name__)


class UploadResult(Enum):
    """Résultat d'un upload."""

    SUCCESS = "success"
    CONNECTION_ERROR = "connection_error"
    AUTH_ERROR = "auth_error"
    UPLOAD_ERROR = "upload_error"
    TIMEOUT = "timeout"


class FtpUploadService:
    """
    Service pour upload FTP/SFTP avec retry et gestion d'erreurs.

    Supporte :
    - FTP via ftplib
    - SFTP via paramiko
    - Multi-volumes (ZIP/RAR)
    - Retry avec backoff exponentiel
    - Logs par job
    """

    def __init__(self):
        """Initialise le service."""
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # secondes
        self.ftp_timeout = 30  # secondes
        self.sftp_timeout = 60  # secondes

    def upload_to_ftp(
        self,
        destination_id: int,
        files: List[Path],
        destination: Optional[Destination] = None,
        job_id: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Upload fichiers vers destination FTP.

        Args:
            destination_id: ID de la destination
            files: Liste des fichiers à uploader
            destination: Instance Destination (optionnel, sera récupérée si None)
            job_id: ID du job pour logging
            max_retries: Nombre max de tentatives (défaut: self.max_retries)

        Returns:
            Tuple (success: bool, message: str)
        """
        if ftplib is None:
            return False, "Module ftplib non disponible"

        if destination is None:
            destination = Destination.query.get(destination_id)
            if not destination:
                return False, f"Destination {destination_id} introuvable"

        if destination.type != "ftp":
            return False, f"Destination {destination_id} n'est pas de type FTP"

        max_retries = max_retries or self.max_retries

        # Trier fichiers pour volumes RAR (.rar puis .r00, .r01, etc.)
        sorted_files = self._sort_files_by_volume(files)

        for attempt in range(max_retries):
            try:
                self._log(
                    job_id,
                    "INFO",
                    f"Tentative upload FTP {attempt + 1}/{max_retries} vers {destination.host}",
                )

                # Connexion FTP
                ftp = ftplib.FTP(timeout=self.ftp_timeout)
                ftp.connect(destination.host, destination.port)
                ftp.login(destination.username, destination.get_password())

                # Changer répertoire si path spécifié
                if destination.path:
                    try:
                        ftp.cwd(destination.path)
                    except ftplib.error_perm:
                        # Essayer de créer le répertoire
                        self._create_ftp_directory(ftp, destination.path)
                        ftp.cwd(destination.path)

                # Upload fichiers
                uploaded_count = 0
                for file_path in sorted_files:
                    if not file_path.exists():
                        self._log(
                            job_id, "WARNING", f"Fichier introuvable: {file_path}"
                        )
                        continue

                    with open(file_path, "rb") as f:
                        filename = file_path.name
                        self._log(
                            job_id,
                            "INFO",
                            f"Upload {filename} ({file_path.stat().st_size} bytes)",
                        )
                        ftp.storbinary(f"STOR {filename}", f)
                        uploaded_count += 1

                ftp.quit()

                self._log(
                    job_id,
                    "INFO",
                    f"Upload FTP réussi: {uploaded_count}/{len(sorted_files)} fichiers",
                )
                return (
                    True,
                    f"Upload réussi: {uploaded_count}/{len(sorted_files)} fichiers",
                )

            except ftplib.error_perm as e:
                error_msg = str(e)
                if "530" in error_msg or "login" in error_msg.lower():
                    self._log(
                        job_id, "ERROR", f"Erreur authentification FTP: {error_msg}"
                    )
                    return False, f"Erreur authentification: {error_msg}"
                else:
                    if attempt < max_retries - 1:
                        delay = self.retry_delays[attempt]
                        self._log(
                            job_id,
                            "WARNING",
                            f"Erreur upload FTP, retry dans {delay}s: {error_msg}",
                        )
                        time.sleep(delay)
                    else:
                        self._log(
                            job_id,
                            "ERROR",
                            f"Erreur upload FTP après {max_retries} tentatives: {error_msg}",
                        )
                        return False, f"Erreur upload: {error_msg}"

            except (ftplib.error_temp, ftplib.error_reply, OSError) as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    delay = self.retry_delays[attempt]
                    self._log(
                        job_id,
                        "WARNING",
                        f"Erreur connexion FTP, retry dans {delay}s: {error_msg}",
                    )
                    time.sleep(delay)
                else:
                    self._log(
                        job_id,
                        "ERROR",
                        f"Erreur connexion FTP après {max_retries} tentatives: {error_msg}",
                    )
                    return False, f"Erreur connexion: {error_msg}"

            except Exception as e:
                error_msg = str(e)
                self._log(job_id, "ERROR", f"Erreur inattendue upload FTP: {error_msg}")
                return False, f"Erreur: {error_msg}"

        return False, "Upload échoué après toutes les tentatives"

    def upload_to_sftp(
        self,
        destination_id: int,
        files: List[Path],
        destination: Optional[Destination] = None,
        job_id: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Upload fichiers vers destination SFTP.

        Args:
            destination_id: ID de la destination
            files: Liste des fichiers à uploader
            destination: Instance Destination (optionnel, sera récupérée si None)
            job_id: ID du job pour logging
            max_retries: Nombre max de tentatives (défaut: self.max_retries)

        Returns:
            Tuple (success: bool, message: str)
        """
        if paramiko is None:
            return False, "Module paramiko non disponible"

        if destination is None:
            destination = Destination.query.get(destination_id)
            if not destination:
                return False, f"Destination {destination_id} introuvable"

        if destination.type != "sftp":
            return False, f"Destination {destination_id} n'est pas de type SFTP"

        max_retries = max_retries or self.max_retries

        # Trier fichiers pour volumes RAR
        sorted_files = self._sort_files_by_volume(files)

        for attempt in range(max_retries):
            try:
                self._log(
                    job_id,
                    "INFO",
                    f"Tentative upload SFTP {attempt + 1}/{max_retries} vers {destination.host}",
                )

                # Connexion SFTP
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=destination.host,
                    port=destination.port,
                    username=destination.username,
                    password=destination.get_password(),
                    timeout=self.sftp_timeout,
                )

                sftp = ssh.open_sftp()

                # Changer répertoire si path spécifié
                if destination.path:
                    try:
                        sftp.chdir(destination.path)
                    except IOError:
                        # Essayer de créer le répertoire
                        self._create_sftp_directory(sftp, destination.path)
                        sftp.chdir(destination.path)

                # Upload fichiers
                uploaded_count = 0
                for file_path in sorted_files:
                    if not file_path.exists():
                        self._log(
                            job_id, "WARNING", f"Fichier introuvable: {file_path}"
                        )
                        continue

                    filename = file_path.name
                    remote_path = f"{filename}"
                    self._log(
                        job_id,
                        "INFO",
                        f"Upload {filename} ({file_path.stat().st_size} bytes)",
                    )
                    sftp.put(str(file_path), remote_path)
                    uploaded_count += 1

                sftp.close()
                ssh.close()

                self._log(
                    job_id,
                    "INFO",
                    f"Upload SFTP réussi: {uploaded_count}/{len(sorted_files)} fichiers",
                )
                return (
                    True,
                    f"Upload réussi: {uploaded_count}/{len(sorted_files)} fichiers",
                )

            except paramiko.AuthenticationException as e:
                error_msg = str(e)
                self._log(job_id, "ERROR", f"Erreur authentification SFTP: {error_msg}")
                return False, f"Erreur authentification: {error_msg}"

            except (paramiko.SSHException, OSError, IOError) as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    delay = self.retry_delays[attempt]
                    self._log(
                        job_id,
                        "WARNING",
                        f"Erreur connexion SFTP, retry dans {delay}s: {error_msg}",
                    )
                    time.sleep(delay)
                else:
                    self._log(
                        job_id,
                        "ERROR",
                        f"Erreur connexion SFTP après {max_retries} tentatives: {error_msg}",
                    )
                    return False, f"Erreur connexion: {error_msg}"

            except Exception as e:
                error_msg = str(e)
                self._log(
                    job_id, "ERROR", f"Erreur inattendue upload SFTP: {error_msg}"
                )
                return False, f"Erreur: {error_msg}"

        return False, "Upload échoué après toutes les tentatives"

    def test_connection(
        self,
        destination: Destination,
    ) -> Tuple[bool, str]:
        """
        Test connexion à une destination FTP/SFTP.

        Args:
            destination: Instance Destination

        Returns:
            Tuple (success: bool, message: str)
        """
        if destination.type == "ftp":
            return self._test_ftp_connection(destination)
        elif destination.type == "sftp":
            return self._test_sftp_connection(destination)
        else:
            return False, f"Type de destination invalide: {destination.type}"

    def _test_ftp_connection(self, destination: Destination) -> Tuple[bool, str]:
        """Test connexion FTP."""
        if ftplib is None:
            return False, "Module ftplib non disponible"

        try:
            ftp = ftplib.FTP(timeout=self.ftp_timeout)
            ftp.connect(destination.host, destination.port)
            ftp.login(destination.username, destination.get_password())
            ftp.quit()
            return True, "Connexion FTP réussie"
        except ftplib.error_perm as e:
            if "530" in str(e) or "login" in str(e).lower():
                return False, f"Erreur authentification: {e}"
            return False, f"Erreur permission: {e}"
        except Exception as e:
            return False, f"Erreur connexion: {e}"

    def _test_sftp_connection(self, destination: Destination) -> Tuple[bool, str]:
        """Test connexion SFTP."""
        if paramiko is None:
            return False, "Module paramiko non disponible"

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=destination.host,
                port=destination.port,
                username=destination.username,
                password=destination.get_password(),
                timeout=self.sftp_timeout,
            )
            ssh.close()
            return True, "Connexion SFTP réussie"
        except paramiko.AuthenticationException as e:
            return False, f"Erreur authentification: {e}"
        except Exception as e:
            return False, f"Erreur connexion: {e}"

    def _sort_files_by_volume(self, files: List[Path]) -> List[Path]:
        """
        Trie les fichiers pour uploader volumes RAR dans l'ordre.

        Ordre : .rar puis .r00, .r01, .r02, etc.

        Args:
            files: Liste des fichiers

        Returns:
            Liste triée
        """

        def sort_key(file_path: Path) -> tuple:
            name = file_path.name.lower()
            ext = file_path.suffix.lower()

            # .rar vient en premier
            if ext == ".rar":
                return (0, name)
            # Puis .r00, .r01, etc.
            elif ext.startswith(".r") and len(ext) == 4 and ext[1:].isdigit():
                volume_num = int(ext[1:])
                return (1, volume_num, name)
            # Autres fichiers
            else:
                return (2, name)

        return sorted(files, key=sort_key)

    def _create_ftp_directory(self, ftp: ftplib.FTP, path: str) -> None:
        """Crée récursivement un répertoire FTP."""
        try:
            parts = path.strip("/").split("/")
            current = ""
            for part in parts:
                if not part:
                    continue
                current += "/" + part
                try:
                    ftp.cwd(current)
                except ftplib.error_perm:
                    ftp.mkd(current)
                    ftp.cwd(current)
        except Exception as e:
            logger.warning(f"Erreur création répertoire FTP {path}: {e}")

    def _create_sftp_directory(self, sftp, path: str) -> None:
        """Crée récursivement un répertoire SFTP."""
        try:
            parts = path.strip("/").split("/")
            current = ""
            for part in parts:
                if not part:
                    continue
                current += "/" + part
                try:
                    sftp.chdir(current)
                except IOError:
                    sftp.mkdir(current)
                    sftp.chdir(current)
        except Exception as e:
            logger.warning(f"Erreur création répertoire SFTP {path}: {e}")

    def _log(self, job_id: Optional[str], level: str, message: str) -> None:
        """
        Log un message dans les job_logs si job_id fourni.

        Args:
            job_id: ID du job
            level: Niveau de log (INFO/WARNING/ERROR)
            message: Message à logger
        """
        if job_id:
            try:
                job = Job.query.filter_by(job_id=job_id).first()
                if job:
                    job.add_log(level, f"[FTP Upload] {message}")
            except Exception as e:
                logger.error(f"Erreur ajout log job {job_id}: {e}")

        # Logger aussi dans le logger Python
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
