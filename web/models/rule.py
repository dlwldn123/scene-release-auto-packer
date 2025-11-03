"""Rule model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from web.extensions import db


class Rule(db.Model):
    """Rule model for Scene rules."""

    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    scene: Mapped[str | None] = mapped_column(db.String(50), nullable=True, index=True)
    section: Mapped[str | None] = mapped_column(db.String(100), nullable=True, index=True)
    year: Mapped[int | None] = mapped_column(db.Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "scene": self.scene,
            "section": self.section,
            "year": self.year,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<Rule {self.name}>"
