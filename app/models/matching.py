"""Current matching cache and request-triggered execution history."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import RecordMixin


class MatchState(Base):
    __tablename__ = "match_states"
    __table_args__ = (
        CheckConstraint("last_completed_user_version > 0", name="version_positive"),
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    last_successful_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_completed_user_version: Mapped[int | None] = mapped_column(BigInteger)
    last_completed_scoring_version: Mapped[str | None] = mapped_column(Text)


class MatchRun(RecordMixin, Base):
    __tablename__ = "match_runs"
    __table_args__ = (
        UniqueConstraint("id", "user_id", "user_matching_version", "scoring_version"),
        CheckConstraint(
            "status IN ('running', 'completed', 'failed', 'superseded')",
            name="status_allowed",
        ),
        CheckConstraint(
            "processed_job_count >= 0 AND user_matching_version > 0",
            name="counts_valid",
        ),
        CheckConstraint(
            "length(trim(scoring_version)) > 0", name="scoring_version_not_blank"
        ),
        CheckConstraint(
            "(status = 'running') = (completed_at IS NULL)", name="completion_state"
        ),
        CheckConstraint("completed_at >= started_at", name="time_order"),
        Index(
            "uq_match_runs_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'running'"),
        ),
        Index("ix_match_runs_user_started", "user_id", "started_at"),
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(Text, server_default=text("'running'"))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    heartbeat_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_matching_version: Mapped[int] = mapped_column(BigInteger)
    scoring_version: Mapped[str] = mapped_column(Text)
    processed_job_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    error_message: Mapped[str | None] = mapped_column(Text)


class MatchResult(Base):
    __tablename__ = "match_results"
    __table_args__ = (
        ForeignKeyConstraint(
            ["match_run_id", "user_id", "user_matching_version", "scoring_version"],
            [
                "match_runs.id",
                "match_runs.user_id",
                "match_runs.user_matching_version",
                "match_runs.scoring_version",
            ],
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "percentage >= 0 AND percentage <= 100", name="percentage_range"
        ),
        CheckConstraint(
            "user_matching_version > 0 AND job_matching_version > 0",
            name="versions_positive",
        ),
        Index("ix_match_results_job_id", "job_id"),
        Index("ix_match_results_run", "match_run_id"),
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    job_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    user_matching_version: Mapped[int] = mapped_column(BigInteger)
    job_matching_version: Mapped[int] = mapped_column(BigInteger)
    scoring_version: Mapped[str] = mapped_column(Text)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    match_run_id: Mapped[int] = mapped_column(BigInteger)


Index(
    "ix_match_results_user_score",
    MatchResult.user_id,
    MatchResult.percentage.desc(),
    MatchResult.job_id,
)
