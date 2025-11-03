"""
Modèle utilisateur avec authentification et rôles.
"""

import enum
from datetime import datetime
from typing import Optional

from werkzeug.security import check_password_hash, generate_password_hash

from web.database import db


class UserRole(enum.Enum):
    """Rôles utilisateur."""

    ADMIN = "admin"
    OPERATOR = "operator"


class User(db.Model):
    """
    Modèle utilisateur avec authentification et rôles.

    Rôles:
    - admin: Accès complet (config système, templates, etc.)
    - operator: Packaging uniquement, pas config système
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.OPERATOR)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relations
    jobs = db.relationship(
        "Job", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    preferences = db.relationship(
        "UserPreference", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    api_configs = db.relationship(
        "ApiConfig", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    destinations = db.relationship(
        "Destination", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    templates = db.relationship(
        "NfoTemplate",
        backref="creator",
        lazy=True,
        foreign_keys="NfoTemplate.created_by",
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role.value})>"

    def set_password(self, password: str) -> None:
        """
        Hash et définit le mot de passe.

        Args:
            password: Mot de passe en clair
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Vérifie le mot de passe.

        Args:
            password: Mot de passe en clair

        Returns:
            True si mot de passe correct
        """
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        """
        Vérifie si l'utilisateur est admin.

        Returns:
            True si admin
        """
        return self.role == UserRole.ADMIN

    def update_last_login(self) -> None:
        """Met à jour la date de dernière connexion."""
        self.last_login = datetime.utcnow()
        db.session.commit()
