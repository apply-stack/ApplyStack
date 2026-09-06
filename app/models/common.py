"""Shared columns for records and CV source content."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, FetchedValue, Identity, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column


class RecordMixin:
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=FetchedValue(),
    )


class MonthRangeMixin:
    # A missing year means the entire date is unknown; no invented day values.
    start_year: Mapped[int | None] = mapped_column(Integer)
    start_month: Mapped[int | None] = mapped_column(Integer)
    end_year: Mapped[int | None] = mapped_column(Integer)
    end_month: Mapped[int | None] = mapped_column(Integer)
    is_current: Mapped[bool] = mapped_column(server_default=text("false"))
