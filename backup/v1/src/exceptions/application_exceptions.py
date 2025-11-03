"""
Exceptions personnalisées pour gestion d'erreurs cohérente.
"""

from typing import Optional


class ApplicationError(Exception):
    """
    Exception de base pour toutes les erreurs de l'application.

    Args:
        message: Message d'erreur descriptif
        error_code: Code d'erreur optionnel pour identification
        details: Détails supplémentaires optionnels
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convertit l'exception en dictionnaire pour sérialisation JSON."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "error_type": self.__class__.__name__,
            "details": self.details,
        }


class ValidationError(ApplicationError):
    """Erreur de validation des données."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        super().__init__(
            message, error_code="VALIDATION_ERROR", details=details, **kwargs
        )


class FileNotFoundError(ApplicationError):
    """Erreur fichier introuvable."""

    def __init__(self, filepath: str, **kwargs):
        super().__init__(
            f"Fichier introuvable: {filepath}",
            error_code="FILE_NOT_FOUND",
            details={"filepath": filepath},
            **kwargs,
        )
        self.filepath = filepath


class ConfigurationError(ApplicationError):
    """Erreur de configuration."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, error_code="CONFIG_ERROR", details=details, **kwargs)


class PackagingError(ApplicationError):
    """Erreur lors du packaging."""

    def __init__(self, message: str, stage: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if stage:
            details["stage"] = stage
        super().__init__(
            message, error_code="PACKAGING_ERROR", details=details, **kwargs
        )


class MetadataError(ApplicationError):
    """Erreur lors de l'extraction de métadonnées."""

    def __init__(self, message: str, format_type: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if format_type:
            details["format_type"] = format_type
        super().__init__(
            message, error_code="METADATA_ERROR", details=details, **kwargs
        )


class APIError(ApplicationError):
    """Erreur lors d'appels API externes."""

    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if provider:
            details["provider"] = provider
        super().__init__(message, error_code="API_ERROR", details=details, **kwargs)
        self.provider = provider
