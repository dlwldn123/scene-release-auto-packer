"""
Utilitaires de chiffrement pour API keys et mots de passe.
"""

import base64
import logging
import os

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EncryptionKeyError(Exception):
    """Exception levée en cas d'erreur avec la clé de chiffrement."""

    pass


def get_encryption_key() -> bytes:
    """
    Récupère ou génère la clé de chiffrement pour les API keys.

    En production, la clé DOIT être fournie via variable d'environnement.
    En développement, une clé auto-générée est utilisée si absente.

    Returns:
        Clé de chiffrement

    Raises:
        EncryptionKeyError: Si clé invalide en production
    """
    key_str = os.getenv("API_KEYS_ENCRYPTION_KEY")
    is_production = (
        os.getenv("FLASK_ENV") == "production"
        or os.getenv("ENVIRONMENT") == "production"
    )

    if key_str:
        # Utiliser la clé fournie
        try:
            decoded_key = base64.urlsafe_b64decode(key_str.encode())
            if len(decoded_key) != 32:
                raise ValueError(
                    f"Clé de chiffrement invalide: longueur doit être 32 bytes, obtenu {len(decoded_key)}"
                )
            return decoded_key
        except Exception as e:
            logger.error(f"Erreur déchiffrement clé API: {e}")
            if is_production:
                raise EncryptionKeyError(
                    f"Clé de chiffrement invalide en production: {e}"
                ) from e
            # En dev, générer une nouvelle clé si invalide
            logger.warning("Clé invalide, génération nouvelle clé (dev uniquement)")
            return Fernet.generate_key()
    else:
        # Générer une clé (à utiliser uniquement en dev)
        if is_production:
            raise EncryptionKeyError(
                "Variable d'environnement API_KEYS_ENCRYPTION_KEY requise en production. "
                'Générer via: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            )
        logger.warning(
            "API_KEYS_ENCRYPTION_KEY non définie, génération clé auto (dev uniquement)"
        )
        return Fernet.generate_key()


def get_cipher() -> Fernet:
    """
    Retourne le cipher Fernet pour chiffrement.

    Returns:
        Instance Fernet
    """
    key = get_encryption_key()
    # Assurer que la clé est de la bonne taille (32 bytes pour Fernet)
    if len(key) != 32:
        key = base64.urlsafe_b64encode(key[:32]).decode()
        key = base64.urlsafe_b64decode(key.encode())
    return Fernet(base64.urlsafe_b64encode(key[:32]))
