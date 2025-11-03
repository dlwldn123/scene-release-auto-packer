"""Group model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from web.extensions import db

# Import association tables
from web.models.associations import user_groups  # noqa: F401


class Group(db.Model):
    """Group model."""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        db.String(80), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    users = db.relationship(
        "User", secondary="user_groups", back_populates="groups", lazy="dynamic"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<Group {self.name}>"
