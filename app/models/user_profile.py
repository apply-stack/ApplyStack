"""Personal details used as the source for CV creation."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    FetchedValue,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_not_blank"),
        CheckConstraint("length(trim(surname)) > 0", name="surname_not_blank"),
        CheckConstraint(
            "country_code IS NULL OR country_code ~ '^[A-Z]{2}$'",
            name="country_code_format",
        ),
        CheckConstraint(
            "contact_email IS NULL OR length(trim(contact_email)) > 0",
            name="contact_email_not_blank",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    user: Mapped["User"] = relationship(back_populates="profile", lazy="raise")
    name: Mapped[str] = mapped_column(Text)
    surname: Mapped[str] = mapped_column(Text)
    headline: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    phone_number: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    country_code: Mapped[str | None] = mapped_column(String(2))
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    github_url: Mapped[str | None] = mapped_column(Text)
    website_url: Mapped[str | None] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=FetchedValue(),
    )

    @validates(
        "headline",
        "summary",
        "phone_number",
        "city",
        "country_code",
        "linkedin_url",
        "github_url",
        "website_url",
        "contact_email",
    )
    def normalize_optional_text(self, key: str, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        return value.upper() if key == "country_code" else value

    def resolve_cv_email(self, login_email: str) -> str:
        """
        Use the current login email as fallback without copying it into storage.

        The caller supplies users.email to avoid implicit database IO in async code.
        """
        return self.contact_email or login_email
