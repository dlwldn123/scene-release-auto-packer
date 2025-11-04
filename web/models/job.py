"""Job model (skeleton for Phase 2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web.extensions import db


class Job(db.Model):
    """Job model."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    release_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("releases.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        db.String(50), default="pending", nullable=False
    )
    job_type: Mapped[str | None] = mapped_column(db.String(50), nullable=True)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    # Relationships
    release = relationship("Release", back_populates="jobs")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "release_id": self.release_id,
            "status": self.status,
            "job_type": self.job_type,
            "config_json": self.config_json,
            "logs": self.logs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }
