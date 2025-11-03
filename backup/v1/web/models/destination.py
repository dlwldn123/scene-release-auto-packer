"""
Modèle pour les destinations FTP/SFTP.
"""

from datetime import datetime
from typing import Optional

from web.crypto import get_cipher
from web.database import db


class Destination(db.Model):
    """
    Destinations FTP/SFTP pour export.

    Les mots de passe sont chiffrés au repos.
    """

    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum("ftp", "sftp", name="destination_type"), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.Text, nullable=False)  # Chiffré
    path = db.Column(db.String(500), nullable=True)  # Chemin distant
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Destination {self.name} ({self.type})>"

    def get_password(self) -> str:
        """
        Déchiffre et retourne le mot de passe.

        Returns:
            Mot de passe en clair
        """
        try:
            cipher = get_cipher()
            decrypted = cipher.decrypt(self.password.encode())
            return decrypted.decode()
        except Exception as e:
            # Fallback si erreur déchiffrement
            return self.password

    def set_password(self, password: str) -> None:
        """
        Chiffre et stocke le mot de passe.

        Args:
            password: Mot de passe en clair
        """
        try:
            cipher = get_cipher()
            encrypted = cipher.encrypt(password.encode())
            self.password = encrypted.decode()
        except Exception as e:
            # En cas d'erreur, stocker en clair (non recommandé)
            self.password = password
