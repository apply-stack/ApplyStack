"""Reusable education, experience and project content owned by a user."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import MonthRangeMixin, RecordMixin, TimestampMixin


class Education(RecordMixin, TimestampMixin, MonthRangeMixin, Base):
    __tablename__ = "educations"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        Index("ix_educations_user_id", "user_id"),
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
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT")
    )
    institution_name: Mapped[str] = mapped_column(Text)
    degree: Mapped[str] = mapped_column(Text)
    field_of_study: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)


class Experience(RecordMixin, TimestampMixin, MonthRangeMixin, Base):
    __tablename__ = "experiences"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        Index("ix_experiences_user_id", "user_id"),
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
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT")
    )
    company_name: Mapped[str] = mapped_column(Text)
    position_title: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)


class Project(RecordMixin, TimestampMixin, MonthRangeMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        Index("ix_projects_user_id", "user_id"),
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
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT")
    )
    project_name: Mapped[str] = mapped_column(Text)
    project_url: Mapped[str | None] = mapped_column(Text)
    repository_url: Mapped[str | None] = mapped_column(Text)


class ExperienceBullet(RecordMixin, TimestampMixin, Base):
    __tablename__ = "experience_bullets"
    __table_args__ = (
        UniqueConstraint("id", "experience_id"),
        UniqueConstraint("experience_id", "position"),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint("length(trim(content)) > 0", name="content_not_blank"),
    )
    experience_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("experiences.id", ondelete="RESTRICT")
    )
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)


class ProjectBullet(RecordMixin, TimestampMixin, Base):
    __tablename__ = "project_bullets"
    __table_args__ = (
        UniqueConstraint("id", "project_id"),
        UniqueConstraint("project_id", "position"),
        CheckConstraint("position > 0", name="position_positive"),
        CheckConstraint("length(trim(content)) > 0", name="content_not_blank"),
    )
    project_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("projects.id", ondelete="RESTRICT")
    )
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)


class ProjectSkill(Base):
    __tablename__ = "project_skills"
    __table_args__ = (Index("ix_project_skills_skill_id", "skill_id"),)
    project_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skills.skill_id", ondelete="RESTRICT"), primary_key=True
    )
