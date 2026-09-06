"""User account storage. Authentication must require an active, verified account."""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    FetchedValue,
    Identity,
    Index,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class UserStatus(StrEnum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class User(Base):
    __tablename__ = "users"
    profile: Mapped["UserProfile | None"] = relationship(
        back_populates="user", passive_deletes="all", lazy="raise"
    )
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending_verification', 'active', 'suspended', 'deactivated')",
            name="status_allowed",
        ),
        CheckConstraint(
            "status <> 'active' OR email_verified_at IS NOT NULL",
            name="active_requires_verified_email",
        ),
        CheckConstraint("length(trim(email)) > 0", name="email_not_blank"),
        CheckConstraint(
            "length(trim(password_hash)) > 0", name="password_hash_not_blank"
        ),
        CheckConstraint("matching_version > 0", name="matching_version_positive"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    matching_version: Mapped[int] = mapped_column(BigInteger, server_default=text("1"))
    email: Mapped[str] = mapped_column(Text)
    # Store the full encoded Argon2id output, never a plaintext password.
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[str] = mapped_column(
        Text, server_default=text("'pending_verification'")
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=FetchedValue(),
    )


Index("uq_users_email_normalized", func.lower(func.btrim(User.email)), unique=True)
