"""Token blocklist model for JWT revocation."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from web.extensions import db


class TokenBlocklist(db.Model):
    """Token blocklist model for revoked JWT tokens."""

    __tablename__ = "token_blocklist"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    jti: Mapped[str] = mapped_column(
        db.String(36), unique=True, nullable=False, index=True
    )
    token_type: Mapped[str] = mapped_column(db.String(10), nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    revoked_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, index=True
    )

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "jti": self.jti,
            "token_type": self.token_type,
            "user_id": self.user_id,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<TokenBlocklist {self.jti}>"
