"""CV snapshots: source edits never rewrite previously selected content."""

from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import MonthRangeMixin, RecordMixin, TimestampMixin


class CV(RecordMixin, TimestampMixin, Base):
    __tablename__ = "cvs"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        Index("ix_cvs_user_id", "user_id"),
        Index("ix_cvs_target_job_id", "target_job_id"),
        CheckConstraint(
            "length(trim(title)) > 0 AND length(trim(language_code)) > 0 AND length(trim(template_version)) > 0",
            name="required_text",
        ),
        CheckConstraint(
            "status IN ('draft', 'generating', 'ready', 'failed')",
            name="status_allowed",
        ),
        CheckConstraint(
            "jsonb_typeof(header_snapshot) = 'object'", name="header_object"
        ),
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT")
    )
    target_job_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("jobs.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(Text)
    language_code: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default=text("'draft'"))
    template_version: Mapped[str] = mapped_column(Text)
    header_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    pdf_storage_key: Mapped[str | None] = mapped_column(Text)


class CVEducation(RecordMixin, MonthRangeMixin, Base):
    __tablename__ = "cv_educations"
    __table_args__ = (
        UniqueConstraint("cv_id", "source_education_id"),
        UniqueConstraint("cv_id", "position"),
        UniqueConstraint("id", "source_education_id"),
        ForeignKeyConstraint(
            ["cv_id", "user_id"], ["cvs.id", "cvs.user_id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["source_education_id", "user_id"],
            ["educations.id", "educations.user_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_cv_educations_source_owner", "source_education_id", "user_id"),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint(
            "(start_year IS NULL) = (start_month IS NULL) AND (end_year IS NULL) = (end_month IS NULL)",
            name="date_pairs",
        ),
        CheckConstraint(
            "start_month BETWEEN 1 AND 12 AND end_month BETWEEN 1 AND 12 AND start_year BETWEEN 1 AND 9999 AND end_year BETWEEN 1 AND 9999",
            name="date_ranges",
        ),
        CheckConstraint(
            "(end_year, end_month) >= (start_year, start_month)", name="date_order"
        ),
        CheckConstraint(
            "NOT is_current OR end_year IS NULL", name="current_without_end"
        ),
        CheckConstraint(
            "length(trim(institution_name)) > 0", name="institution_name_not_blank"
        ),
        CheckConstraint("length(trim(degree)) > 0", name="degree_not_blank"),
        CheckConstraint(
            "length(trim(field_of_study)) > 0", name="field_of_study_not_blank"
        ),
    )
    cv_id: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(BigInteger)
    source_education_id: Mapped[int] = mapped_column(BigInteger)
    position: Mapped[int] = mapped_column(Integer)
    institution_name: Mapped[str] = mapped_column(Text)
    degree: Mapped[str] = mapped_column(Text)
    field_of_study: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)


class CVExperience(RecordMixin, MonthRangeMixin, Base):
    __tablename__ = "cv_experiences"
    __table_args__ = (
        UniqueConstraint("cv_id", "source_experience_id"),
        UniqueConstraint("cv_id", "position"),
        UniqueConstraint("id", "source_experience_id"),
        ForeignKeyConstraint(
            ["cv_id", "user_id"], ["cvs.id", "cvs.user_id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["source_experience_id", "user_id"],
            ["experiences.id", "experiences.user_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_cv_experiences_source_owner", "source_experience_id", "user_id"),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint(
            "(start_year IS NULL) = (start_month IS NULL) AND (end_year IS NULL) = (end_month IS NULL)",
            name="date_pairs",
        ),
        CheckConstraint(
            "start_month BETWEEN 1 AND 12 AND end_month BETWEEN 1 AND 12 AND start_year BETWEEN 1 AND 9999 AND end_year BETWEEN 1 AND 9999",
            name="date_ranges",
        ),
        CheckConstraint(
            "(end_year, end_month) >= (start_year, start_month)", name="date_order"
        ),
        CheckConstraint(
            "NOT is_current OR end_year IS NULL", name="current_without_end"
        ),
        CheckConstraint(
            "length(trim(company_name)) > 0", name="company_name_not_blank"
        ),
        CheckConstraint(
            "length(trim(position_title)) > 0", name="position_title_not_blank"
        ),
    )
    cv_id: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(BigInteger)
    source_experience_id: Mapped[int] = mapped_column(BigInteger)
    position: Mapped[int] = mapped_column(Integer)
    company_name: Mapped[str] = mapped_column(Text)
    position_title: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)


class CVProject(RecordMixin, MonthRangeMixin, Base):
    __tablename__ = "cv_projects"
    __table_args__ = (
        UniqueConstraint("cv_id", "source_project_id"),
        UniqueConstraint("cv_id", "position"),
        UniqueConstraint("id", "source_project_id"),
        ForeignKeyConstraint(
            ["cv_id", "user_id"], ["cvs.id", "cvs.user_id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["source_project_id", "user_id"],
            ["projects.id", "projects.user_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_cv_projects_source_owner", "source_project_id", "user_id"),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint(
            "(start_year IS NULL) = (start_month IS NULL) AND (end_year IS NULL) = (end_month IS NULL)",
            name="date_pairs",
        ),
        CheckConstraint(
            "start_month BETWEEN 1 AND 12 AND end_month BETWEEN 1 AND 12 AND start_year BETWEEN 1 AND 9999 AND end_year BETWEEN 1 AND 9999",
            name="date_ranges",
        ),
        CheckConstraint(
            "(end_year, end_month) >= (start_year, start_month)", name="date_order"
        ),
        CheckConstraint(
            "NOT is_current OR end_year IS NULL", name="current_without_end"
        ),
        CheckConstraint(
            "length(trim(project_name)) > 0", name="project_name_not_blank"
        ),
    )
    cv_id: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(BigInteger)
    source_project_id: Mapped[int] = mapped_column(BigInteger)
    position: Mapped[int] = mapped_column(Integer)
    project_name: Mapped[str] = mapped_column(Text)
    project_url: Mapped[str | None] = mapped_column(Text)
    repository_url: Mapped[str | None] = mapped_column(Text)


class CVExperienceBullet(RecordMixin, Base):
    __tablename__ = "cv_experience_bullets"
    __table_args__ = (
        UniqueConstraint("cv_experience_id", "source_bullet_id"),
        UniqueConstraint("cv_experience_id", "position"),
        ForeignKeyConstraint(
            ["cv_experience_id", "source_experience_id"],
            ["cv_experiences.id", "cv_experiences.source_experience_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["source_bullet_id", "source_experience_id"],
            ["experience_bullets.id", "experience_bullets.experience_id"],
            ondelete="RESTRICT",
        ),
        Index(
            "ix_cv_experience_bullets_source",
            "source_bullet_id",
            "source_experience_id",
        ),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint("length(trim(content)) > 0", name="content_not_blank"),
    )
    cv_experience_id: Mapped[int] = mapped_column(BigInteger)
    source_experience_id: Mapped[int] = mapped_column(BigInteger)
    source_bullet_id: Mapped[int] = mapped_column(BigInteger)
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)


class CVProjectBullet(RecordMixin, Base):
    __tablename__ = "cv_project_bullets"
    __table_args__ = (
        UniqueConstraint("cv_project_id", "source_bullet_id"),
        UniqueConstraint("cv_project_id", "position"),
        ForeignKeyConstraint(
            ["cv_project_id", "source_project_id"],
            ["cv_projects.id", "cv_projects.source_project_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["source_bullet_id", "source_project_id"],
            ["project_bullets.id", "project_bullets.project_id"],
            ondelete="RESTRICT",
        ),
        Index("ix_cv_project_bullets_source", "source_bullet_id", "source_project_id"),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint("length(trim(content)) > 0", name="content_not_blank"),
    )
    cv_project_id: Mapped[int] = mapped_column(BigInteger)
    source_project_id: Mapped[int] = mapped_column(BigInteger)
    source_bullet_id: Mapped[int] = mapped_column(BigInteger)
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)


class CVSkill(Base):
    __tablename__ = "cv_skills"
    __table_args__ = (
        UniqueConstraint("cv_id", "category", "position"),
        Index("ix_cv_skills_skill_id", "skill_id"),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint(
            "length(trim(display_name)) > 0", name="display_name_not_blank"
        ),
        CheckConstraint(
            "category IN ('languages', 'frameworks', 'developer_tools', 'libraries')",
            name="category_allowed",
        ),
    )
    cv_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("cvs.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skills.skill_id", ondelete="RESTRICT"), primary_key=True
    )
    category: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)
    display_name: Mapped[str] = mapped_column(Text)
