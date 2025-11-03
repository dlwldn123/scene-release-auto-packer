"""
Modèle pour les templates NFO.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from web.database import db


class NfoTemplate(db.Model):
    """
    Template NFO avec placeholders.

    Permet de générer des NFO personnalisés avec variables.
    """

    __tablename__ = "nfo_templates"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)  # Template avec placeholders
    variables = db.Column(db.JSON, nullable=True)  # Liste variables disponibles
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<NfoTemplate {self.name}>"

    def get_variables(self) -> Dict[str, Any]:
        """
        Retourne la liste des variables disponibles.

        Returns:
            Dictionnaire de variables
        """
        if isinstance(self.variables, str):
            return json.loads(self.variables)
        return self.variables or {}

    def set_variables(self, variables: Dict[str, Any]) -> None:
        """
        Définit les variables disponibles.

        Args:
            variables: Dictionnaire de variables
        """
        self.variables = variables
