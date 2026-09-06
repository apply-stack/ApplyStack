"""
Create cv educations.

Revision ID: e48c26e96f18
Revises: 09df6f5a00c8
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e48c26e96f18"
down_revision: str | Sequence[str] | None = "09df6f5a00c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cv_educations",
        sa.Column("cv_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("source_education_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("institution_name", sa.Text(), nullable=False),
        sa.Column("degree", sa.Text(), nullable=False),
        sa.Column("field_of_study", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("start_year", sa.Integer(), nullable=True),
        sa.Column("start_month", sa.Integer(), nullable=True),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("end_month", sa.Integer(), nullable=True),
        sa.Column(
            "is_current", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.CheckConstraint(
            "(end_year, end_month) >= (start_year, start_month)",
            name=op.f("ck_cv_educations_date_order"),
        ),
        sa.CheckConstraint(
            "(start_year IS NULL) = (start_month IS NULL) AND (end_year IS NULL) = (end_month IS NULL)",
            name=op.f("ck_cv_educations_date_pairs"),
        ),
        sa.CheckConstraint(
            "NOT is_current OR end_year IS NULL",
            name=op.f("ck_cv_educations_current_without_end"),
        ),
        sa.CheckConstraint(
            "length(trim(degree)) > 0", name=op.f("ck_cv_educations_degree_not_blank")
        ),
        sa.CheckConstraint(
            "length(trim(field_of_study)) > 0",
            name=op.f("ck_cv_educations_field_of_study_not_blank"),
        ),
        sa.CheckConstraint(
            "length(trim(institution_name)) > 0",
            name=op.f("ck_cv_educations_institution_name_not_blank"),
        ),
        sa.CheckConstraint(
            "position > 0", name=op.f("ck_cv_educations_position_positive")
        ),
        sa.CheckConstraint(
            "start_month BETWEEN 1 AND 12 AND end_month BETWEEN 1 AND 12 AND start_year BETWEEN 1 AND 9999 AND end_year BETWEEN 1 AND 9999",
            name=op.f("ck_cv_educations_date_ranges"),
        ),
        sa.ForeignKeyConstraint(
            ["cv_id", "user_id"],
            ["cvs.id", "cvs.user_id"],
            name=op.f("fk_cv_educations_cv_id_cvs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_education_id", "user_id"],
            ["educations.id", "educations.user_id"],
            name=op.f("fk_cv_educations_source_education_id_educations"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cv_educations")),
        sa.UniqueConstraint(
            "cv_id", "position", name=op.f("uq_cv_educations_cv_id_position")
        ),
        sa.UniqueConstraint(
            "cv_id",
            "source_education_id",
            name=op.f("uq_cv_educations_cv_id_source_education_id"),
        ),
        sa.UniqueConstraint(
            "id",
            "source_education_id",
            name=op.f("uq_cv_educations_id_source_education_id"),
        ),
    )
    op.create_index(
        "ix_cv_educations_source_owner",
        "cv_educations",
        ["source_education_id", "user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cv_educations_source_owner", table_name="cv_educations")
    op.drop_table("cv_educations")
