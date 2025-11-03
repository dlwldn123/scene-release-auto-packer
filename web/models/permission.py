"""Permission model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from web.extensions import db

# Import association tables
from web.models.associations import role_permissions  # noqa: F401


class Permission(db.Model):
    """Permission model."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    resource: Mapped[str] = mapped_column(db.String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(db.String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    roles = db.relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="dynamic",
    )

    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint("resource", "action", name="uq_permission"),)

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "resource": self.resource,
            "action": self.action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<Permission {self.resource}:{self.action}>"
