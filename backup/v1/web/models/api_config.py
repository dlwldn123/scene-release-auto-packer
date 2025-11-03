"""
Modèle pour la configuration des APIs externes.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from web.crypto import get_cipher
from web.database import db


class ApiConfig(db.Model):
    """
    Configuration des APIs externes (OMDb, TVDB, TMDb, OpenLibrary).

    Les clés API sont chiffrées au repos.
    """

    __tablename__ = "api_configs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True, index=True
    )  # NULL = global
    api_name = db.Column(db.String(50), nullable=False)  # omdb/tvdb/tmdb/openlibrary
    api_key = db.Column(db.Text, nullable=False)  # JSON chiffré
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "api_name", name="uq_user_api"),)

    def __repr__(self) -> str:
        return f"<ApiConfig {self.api_name} for user {self.user_id}>"

    def get_api_key(self) -> Dict[str, Any]:
        """
        Déchiffre et retourne la clé API.

        Returns:
            Dictionnaire avec clé API et autres configs
        """
        try:
            cipher = get_cipher()
            decrypted = cipher.decrypt(self.api_key.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            # Fallback si erreur déchiffrement
            return {}

    def set_api_key(self, api_data: Dict[str, Any]) -> None:
        """
        Chiffre et stocke la clé API.

        Args:
            api_data: Dictionnaire avec clé API et autres configs
        """
        try:
            cipher = get_cipher()
            encrypted = cipher.encrypt(json.dumps(api_data).encode())
            self.api_key = encrypted.decode()
        except Exception as e:
            # En cas d'erreur, stocker en clair (non recommandé)
            self.api_key = json.dumps(api_data)
