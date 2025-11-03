"""
Module d'exceptions personnalisées pour Scene Ebook Packer.
"""

from typing import Optional


class ApplicationError(Exception):
    """
    Exception de base pour toutes les erreurs de l'application.

    Attributes:
        message: Message d'erreur
        error_type: Type d'erreur (pour API)
        status_code: Code HTTP (défaut 400)
        field: Champ concerné (optionnel)
        value: Valeur problématique (optionnel)
    """

    def __init__(
        self,
        message: str,
        error_type: str = "ApplicationError",
        status_code: int = 400,
        field: Optional[str] = None,
        value: Optional[str] = None,
    ):
        """
        Initialise l'exception.

        Args:
            message: Message d'erreur
            error_type: Type d'erreur
            status_code: Code HTTP
            field: Champ concerné (optionnel)
            value: Valeur problématique (optionnel)
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.field = field
        self.value = value

    def to_dict(self) -> dict:
        """
        Convertit l'exception en dictionnaire pour réponse JSON.

        Returns:
            Dictionnaire avec success=False, error, error_type, etc.
        """
        result = {
            "success": False,
            "error": self.message,
            "error_type": self.error_type,
        }
        if self.field:
            result["field"] = self.field
        if self.value is not None:
            result["value"] = self.value
        return result


class ValidationError(ApplicationError):
    """Erreur de validation de données."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            error_type="ValidationError",
            status_code=400,
            field=field,
            value=value,
        )


class ConfigurationError(ApplicationError):
    """Erreur de configuration."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_type="ConfigurationError",
            status_code=500,
        )


class FileNotFoundError(ApplicationError):
    """Fichier introuvable (pour éviter conflit avec builtin)."""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"Fichier introuvable: {file_path}",
            error_type="FileNotFoundError",
            status_code=404,
            field="file_path",
            value=file_path,
        )


class PackagingError(ApplicationError):
    """Erreur lors du packaging."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            error_type="PackagingError",
            status_code=500,
        )
        self.details = details

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.details:
            result["details"] = self.details
        return result


class MetadataError(ApplicationError):
    """Erreur lors de l'extraction de métadonnées."""

    def __init__(self, message: str, format_type: Optional[str] = None):
        super().__init__(
            message=message,
            error_type="MetadataError",
            status_code=500,
        )
        self.format_type = format_type

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.format_type:
            result["format_type"] = self.format_type
        return result


class APIError(ApplicationError):
    """Erreur lors d'appels API externes."""

    def __init__(self, message: str, provider: Optional[str] = None):
        super().__init__(
            message=message,
            error_type="APIError",
            status_code=502,
        )
        self.provider = provider

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.provider:
            result["provider"] = self.provider
        return result
