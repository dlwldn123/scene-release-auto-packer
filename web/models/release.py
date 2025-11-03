"""Release model (skeleton for Phase 2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from web.extensions import db


class Release(db.Model):
    """Release model."""

    __tablename__ = "releases"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    group_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("groups.id"), nullable=True
    )
    release_type: Mapped[str] = mapped_column(db.String(50), nullable=False)
    status: Mapped[str] = mapped_column(db.String(50), default="draft", nullable=False)
    release_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=True)
    file_path: Mapped[str | None] = mapped_column(db.String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "group_id": self.group_id,
            "release_type": self.release_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
