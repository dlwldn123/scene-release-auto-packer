"""
Service de packaging synchrone avec gestion de jobs.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.packaging.docs_packer import pack_docs_release
from src.packer import process_ebook
from src.video import pack_tv_release
from web.database import db
from web.models.destination import Destination
from web.models.job import Artifact, Job, JobLog, JobStatus
from web.models.user import User

logger = logging.getLogger(__name__)


class PackagingService:
    """
    Service de packaging synchrone avec création de jobs.

    Intègre le système de jobs existant avec le packaging d'eBooks et TV.
    """

    def __init__(self, user_id: int):
        """
        Initialise le service avec un utilisateur.

        Args:
            user_id: ID de l'utilisateur qui lance le packaging
        """
        self.user_id = user_id
        self.user = User.query.get(user_id)
        if not self.user:
            raise ValueError(f"Utilisateur {user_id} introuvable")

    def create_job(
        self,
        job_type: str,
        group_name: str,
        config: Dict[str, Any],
    ) -> Job:
        """
        Crée un nouveau job de packaging.

        Args:
            job_type: Type de release (TV/EBOOK/DOCS)
            group_name: Nom du groupe Scene
            config: Configuration complète du job

        Returns:
            Instance Job créée
        """
        job = Job(
            job_id=str(uuid.uuid4()),
            user_id=self.user_id,
            status=JobStatus.PENDING,
            type=job_type,
            group_name=group_name,
            config=config,
        )

        db.session.add(job)
        db.session.commit()

        job.add_log("INFO", f"Job créé: {job.job_id}")
        logger.info(f"Job créé: {job.job_id} par utilisateur {self.user_id}")

        return job

    def pack_ebook(
        self,
        ebook_path: str | Path,
        group: str,
        output_dir: Optional[str | Path] = None,
        source_type: Optional[str] = None,
        url: Optional[str] = None,
        enable_api: bool = True,
        nfo_template_path: Optional[str | Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Job:
        """
        Packager un eBook en release Scene avec création de job.

        Args:
            ebook_path: Chemin fichier eBook
            group: Tag groupe Scene
            output_dir: Dossier sortie
            source_type: Type source (RETAIL, SCAN, HYBRID)
            url: URL release
            enable_api: Activer enrichissement API
            nfo_template_path: Chemin template NFO
            config: Configuration supplémentaire

        Returns:
            Job créé et exécuté
        """
        ebook_path = Path(ebook_path)

        if not ebook_path.exists():
            raise FileNotFoundError(f"eBook introuvable: {ebook_path}")

        # Configuration job
        job_config = {
            "ebook_path": str(ebook_path),
            "group": group,
            "output_dir": str(output_dir) if output_dir else None,
            "source_type": source_type,
            "url": url,
            "enable_api": enable_api,
            "nfo_template_path": str(nfo_template_path) if nfo_template_path else None,
            "config": config or {},
        }

        # Créer job
        job = self.create_job(
            job_type="EBOOK",
            group_name=group,
            config=job_config,
        )

        try:
            # Marquer job comme démarré
            job.start()
            job.add_log("INFO", f"Démarrage packaging eBook: {ebook_path.name}")

            # Packager
            release_name = process_ebook(
                ebook_path=ebook_path,
                group=group,
                output_dir=output_dir,
                source_type=source_type,
                url=url,
                enable_api=enable_api,
                config=config,
                verbose=False,
                nfo_template_path=nfo_template_path,
            )

            job.add_log("INFO", f"Packaging terminé: {release_name}")

            # Déterminer le dossier de release
            if output_dir:
                release_dir = Path(output_dir) / release_name
            else:
                release_dir = Path("releases") / release_name

            # Enregistrer artefacts
            self._register_artifacts(job, release_name, release_dir)

            # Marquer comme terminé
            job.complete(release_name=release_name)

            # Upload FTP/SFTP si destination configurée
            self._upload_to_destination(job, release_dir)

            logger.info(f"Job {job.job_id} terminé avec succès: {release_name}")

        except Exception as e:
            error_msg = str(e)
            job.add_log("ERROR", f"Erreur packaging: {error_msg}")
            job.fail(error_msg)
            logger.error(f"Job {job.job_id} échoué: {error_msg}", exc_info=True)
            raise

        return job

    def pack_tv(
        self,
        input_mkv: str | Path,
        release_name: str,
        link: Optional[str] = None,
        profile: Optional[str] = None,
        output_dir: Optional[str | Path] = None,
        enable_api: bool = True,
    ) -> Job:
        """
        Packager une vidéo TV en release Scene avec création de job.

        Args:
            input_mkv: Chemin fichier vidéo
            release_name: Nom de la release
            link: URL release
            profile: Profil (HDTV_720P, etc.)
            output_dir: Dossier sortie
            enable_api: Activer enrichissement APIs TV

        Returns:
            Job créé et exécuté
        """
        input_mkv = Path(input_mkv)

        if not input_mkv.exists():
            raise FileNotFoundError(f"Fichier vidéo introuvable: {input_mkv}")

        # Extraire groupe depuis release_name
        group = release_name.split("-")[-1] if "-" in release_name else "UNKNOWN"

        # Enrichissement métadonnées via APIs TV si activé
        tv_metadata = {}
        if enable_api:
            try:
                from src.metadata.tv_apis import TvApiEnricher
                from web.utils.api_config import (
                    get_tv_api_config,
                    parse_tv_release_name,
                )

                # Récupérer configs API
                api_configs = get_tv_api_config(user_id=self.user_id)

                if api_configs:
                    # Parser release_name pour extraire titre/saison/épisode
                    parsed = parse_tv_release_name(release_name)

                    if parsed.get("title"):
                        # Créer enrichisseur (sans cache pour l'instant, peut être ajouté plus tard)
                        enricher = TvApiEnricher(cache=None)

                        # Enrichir
                        tv_metadata = enricher.enrich(
                            title=parsed["title"],
                            season=parsed.get("season"),
                            episode=parsed.get("episode"),
                            config=api_configs,
                        )

                        if tv_metadata:
                            logger.info(
                                f"Métadonnées TV enrichies depuis: {', '.join(tv_metadata.get('sources', []))}"
                            )
                        else:
                            logger.debug("Aucune métadonnée TV trouvée via APIs")
                else:
                    logger.debug("Aucune config API TV disponible")
            except Exception as e:
                logger.warning(f"Erreur enrichissement TV APIs: {e}", exc_info=True)

        # Configuration job
        job_config = {
            "input_mkv": str(input_mkv),
            "release_name": release_name,
            "link": link,
            "profile": profile,
            "output_dir": str(output_dir) if output_dir else None,
            "tv_metadata": tv_metadata,  # Ajouter métadonnées enrichies
        }

        # Créer job
        job = self.create_job(
            job_type="TV",
            group_name=group,
            config=job_config,
        )

        try:
            # Marquer job comme démarré
            job.start()
            job.add_log("INFO", f"Démarrage packaging TV: {input_mkv.name}")

            if tv_metadata and tv_metadata.get("sources"):
                job.add_log(
                    "INFO",
                    f'Métadonnées TV enrichies depuis: {", ".join(tv_metadata.get("sources", []))}',
                )

            # Packager avec métadonnées enrichies
            release_dir = pack_tv_release(
                input_mkv=input_mkv,
                release_name=release_name,
                link=link,
                profile=profile,
                tv_metadata=tv_metadata,  # Passer métadonnées
            )

            job.add_log("INFO", f"Packaging TV terminé: {release_dir}")

            # Enregistrer artefacts
            self._register_artifacts(job, release_name, release_dir)

            # Marquer comme terminé
            job.complete(release_name=release_name)

            # Upload FTP/SFTP si destination configurée
            self._upload_to_destination(job, release_dir)

            logger.info(f"Job {job.job_id} terminé avec succès: {release_name}")

        except Exception as e:
            error_msg = str(e)
            job.add_log("ERROR", f"Erreur packaging TV: {error_msg}")
            job.fail(error_msg)
            logger.error(f"Job {job.job_id} échoué: {error_msg}", exc_info=True)
            raise

        return job

    def pack_docs(
        self,
        doc_path: str | Path,
        group: str,
        output_dir: Optional[str | Path] = None,
        source_type: Optional[str] = None,
        url: Optional[str] = None,
        nfo_template_path: Optional[str | Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Job:
        """
        Packager un document en release Scene DOCS avec création de job.

        Args:
            doc_path: Chemin fichier document
            group: Tag groupe Scene
            output_dir: Dossier sortie
            source_type: Type source (RETAIL, SCAN, HYBRID)
            url: URL release
            nfo_template_path: Chemin template NFO
            config: Configuration supplémentaire

        Returns:
            Job créé et exécuté
        """
        doc_path = Path(doc_path)

        if not doc_path.exists():
            raise FileNotFoundError(f"Document introuvable: {doc_path}")

        # Configuration job
        job_config = {
            "doc_path": str(doc_path),
            "group": group,
            "output_dir": str(output_dir) if output_dir else None,
            "source_type": source_type,
            "url": url,
            "nfo_template_path": str(nfo_template_path) if nfo_template_path else None,
            "config": config or {},
        }

        # Créer job
        job = self.create_job(
            job_type="DOCS",
            group_name=group,
            config=job_config,
        )

        try:
            # Marquer job comme démarré
            job.start()
            job.add_log("INFO", f"Démarrage packaging DOCS: {doc_path.name}")

            # Packager
            release_name = pack_docs_release(
                doc_path=doc_path,
                group=group,
                output_dir=output_dir,
                source_type=source_type,
                url=url,
                config=config,
                nfo_template_path=nfo_template_path,
            )

            job.add_log("INFO", f"Packaging DOCS terminé: {release_name}")

            # Déterminer le dossier de release
            if output_dir:
                release_dir = Path(output_dir) / release_name
            else:
                release_dir = Path("releases") / release_name

            # Enregistrer artefacts
            self._register_artifacts(job, release_name, release_dir)

            # Marquer comme terminé
            job.complete(release_name=release_name)

            # Upload FTP/SFTP si destination configurée
            self._upload_to_destination(job, release_dir)

            logger.info(f"Job {job.job_id} terminé avec succès: {release_name}")

        except Exception as e:
            error_msg = str(e)
            job.add_log("ERROR", f"Erreur packaging DOCS: {error_msg}")
            job.fail(error_msg)
            logger.error(f"Job {job.job_id} échoué: {error_msg}", exc_info=True)
            raise

        return job

    def _upload_to_destination(
        self,
        job: Job,
        release_dir: Path,
    ) -> None:
        """
        Upload automatique vers destination FTP/SFTP si configurée.

        Args:
            job: Job terminé
            release_dir: Dossier de la release
        """
        try:
            # Chercher destination pour ce groupe (nom contenant le groupe ou exact)
            destination = None

            # Essayer par nom contenant le groupe
            destination = Destination.query.filter(
                Destination.user_id == self.user_id,
                Destination.name.contains(job.group_name),
            ).first()

            if not destination:
                # Chercher par nom exact
                destination = Destination.query.filter_by(
                    user_id=self.user_id,
                    name=job.group_name,
                ).first()

            if not destination:
                # Chercher destination par défaut (première disponible)
                destination = Destination.query.filter_by(
                    user_id=self.user_id,
                ).first()

            if not destination:
                logger.debug(
                    f"Aucune destination configurée pour job {job.job_id}, groupe {job.group_name}"
                )
                return

            # Collecter tous les fichiers à uploader
            # Note: job.artifacts déjà chargé (relation lazy mais job fraîchement créé)
            files_to_upload = []
            for artifact in job.artifacts:
                file_path = release_dir / artifact.file_path
                if file_path.exists():
                    files_to_upload.append(file_path)

            if not files_to_upload:
                logger.warning(f"Aucun fichier à uploader pour job {job.job_id}")
                return

            # Upload selon type destination
            from web.services.ftp_upload import FtpUploadService

            upload_service = FtpUploadService()

            if destination.type == "ftp":
                success, message = upload_service.upload_to_ftp(
                    destination_id=destination.id,
                    files=files_to_upload,
                    destination=destination,
                    job_id=job.job_id,
                )
            elif destination.type == "sftp":
                success, message = upload_service.upload_to_sftp(
                    destination_id=destination.id,
                    files=files_to_upload,
                    destination=destination,
                    job_id=job.job_id,
                )
            else:
                logger.warning(f"Type destination non supporté: {destination.type}")
                return

            if success:
                job.add_log(
                    "INFO", f"Upload {destination.type.upper()} réussi: {message}"
                )
            else:
                job.add_log(
                    "WARNING", f"Upload {destination.type.upper()} échoué: {message}"
                )

        except Exception as e:
            error_msg = f"Erreur upload destination: {str(e)}"
            logger.error(error_msg, exc_info=True)
            job.add_log("WARNING", error_msg)

    def _register_artifacts(
        self,
        job: Job,
        release_name: str,
        release_dir: Optional[str | Path],
    ) -> None:
        """
        Enregistre les artefacts générés dans la base de données.

        Args:
            job: Job associé
            release_name: Nom de la release
            release_dir: Dossier de la release
        """
        if not release_dir:
            return

        release_dir = Path(release_dir)

        if not release_dir.exists():
            return

        # Types de fichiers à enregistrer
        file_types = {
            ".zip": "zip",
            ".rar": "rar",
            ".r00": "rar",
            ".r01": "rar",
            ".nfo": "nfo",
            ".diz": "diz",
            ".sfv": "sfv",
        }

        # Parcourir fichiers
        for file_path in release_dir.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in file_types:
                    file_type = file_types[ext]

                    # Calculer CRC32 (optionnel)
                    crc32 = None
                    try:
                        import zlib

                        with open(file_path, "rb") as f:
                            crc32 = format(zlib.crc32(f.read()) & 0xFFFFFFFF, "08x")
                    except (IOError, OSError, MemoryError) as e:
                        logger.debug(f"Erreur calcul CRC32 pour {file_path}: {e}")
                        # Continuer sans CRC32 si erreur

                    # Créer artefact
                    artifact = Artifact(
                        job_id=job.id,
                        file_path=str(file_path.relative_to(release_dir)),
                        file_type=file_type,
                        file_size=file_path.stat().st_size,
                        crc32=crc32,
                    )
                    db.session.add(artifact)

        db.session.commit()
