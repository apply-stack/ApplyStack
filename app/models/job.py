from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import RecordMixin, TimestampMixin


class Job(RecordMixin, TimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source", "source_job_id"),
        CheckConstraint(
            "length(trim(job_title)) > 0 AND length(trim(company_name)) > 0 AND length(trim(job_description)) > 0 AND length(trim(application_url)) > 0 AND length(trim(source)) > 0",
            name="required_text",
        ),
        CheckConstraint(
            "length(trim(source_job_id)) > 0", name="source_job_id_not_blank"
        ),
        CheckConstraint(
            "application_end_date >= application_start_date", name="date_order"
        ),
        CheckConstraint(
            "work_mode IN ('remote', 'hybrid', 'onsite')", name="work_mode_allowed"
        ),
        CheckConstraint(
            "employment_type IN ('internship', 'full_time', 'part_time', 'contract')",
            name="employment_type_allowed",
        ),
        CheckConstraint(
            "status IN ('open', 'closed', 'unknown')", name="status_allowed"
        ),
        CheckConstraint(
            "skill_extraction_status IN ('pending', 'completed', 'failed')",
            name="extraction_status_allowed",
        ),
        CheckConstraint("matching_version > 0", name="matching_version_positive"),
        Index("ix_jobs_matching_candidates", "status", "skill_extraction_status", "id"),
        Index("ix_jobs_created_at", "created_at"),
    )
    job_title: Mapped[str] = mapped_column(Text)
    company_name: Mapped[str] = mapped_column(Text)
    job_description: Mapped[str] = mapped_column(Text)
    application_url: Mapped[str] = mapped_column(Text)
    application_start_date: Mapped[date | None] = mapped_column(Date)
    application_end_date: Mapped[date | None] = mapped_column(Date)
    location: Mapped[str | None] = mapped_column(Text)
    work_mode: Mapped[str | None] = mapped_column(Text)
    employment_type: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    source_job_id: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default=text("'unknown'"))
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    matching_version: Mapped[int] = mapped_column(BigInteger, server_default=text("1"))
    skill_extraction_status: Mapped[str] = mapped_column(
        Text, server_default=text("'pending'")
    )


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (Index("ix_job_skills_skill_id", "skill_id"),)
    job_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skills.skill_id", ondelete="RESTRICT"), primary_key=True
    )
    is_required: Mapped[bool] = mapped_column()
