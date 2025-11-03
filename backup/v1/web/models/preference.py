"""
Modèles pour les préférences utilisateur et globales.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from web.database import db


class UserPreference(db.Model):
    """
    Préférences utilisateur spécifiques.

    Clé: group+type+rules+template (format configurable)
    Valeur: JSON avec préférences
    """

    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    preference_key = db.Column(db.String(100), nullable=False)
    preference_value = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "preference_key", name="uq_user_preference_key"),
    )

    def __repr__(self) -> str:
        return f"<UserPreference {self.preference_key} for user {self.user_id}>"

    def get_value(self) -> Dict[str, Any]:
        """
        Retourne la valeur de la préférence.

        Returns:
            Dictionnaire de préférences
        """
        if isinstance(self.preference_value, str):
            return json.loads(self.preference_value)
        return self.preference_value or {}

    def set_value(self, value: Dict[str, Any]) -> None:
        """
        Définit la valeur de la préférence.

        Args:
            value: Dictionnaire de préférences
        """
        self.preference_value = value
        self.updated_at = datetime.utcnow()


class GlobalPreference(db.Model):
    """
    Préférences globales (fallback si préférence utilisateur absente).

    Utilisées comme valeurs par défaut.
    """

    __tablename__ = "global_preferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    preference_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    preference_value = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<GlobalPreference {self.preference_key}>"

    def get_value(self) -> Dict[str, Any]:
        """
        Retourne la valeur de la préférence globale.

        Returns:
            Dictionnaire de préférences
        """
        if isinstance(self.preference_value, str):
            return json.loads(self.preference_value)
        return self.preference_value or {}

    def set_value(self, value: Dict[str, Any]) -> None:
        """
        Définit la valeur de la préférence globale.

        Args:
            value: Dictionnaire de préférences
        """
        self.preference_value = value
        self.updated_at = datetime.utcnow()
