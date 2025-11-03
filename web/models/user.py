"""User model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from web.extensions import db

# Import association tables
from web.models.associations import user_groups, user_roles  # noqa: F401


class User(db.Model):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        db.String(80), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(db.String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    note: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    modify_at: Mapped[datetime | None] = mapped_column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )

    # Relationships
    roles = db.relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="dynamic",
    )
    groups = db.relationship(
        "Group",
        secondary="user_groups",
        back_populates="users",
        lazy="dynamic",
    )

    def set_password(self, password: str) -> None:
        """Set password hash.

        Args:
            password: Plain text password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check password.

        Args:
            password: Plain text password.

        Returns:
            True if password matches.
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "active": self.active,
            "note": self.note,
            "roles": [role.to_dict() for role in self.roles.all()],
            "groups": [group.to_dict() for group in self.groups.all()],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modify_at": self.modify_at.isoformat() if self.modify_at else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<User {self.username}>"
