"""
Create cv experiences.

Revision ID: eba2586cde39
Revises: e48c26e96f18
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "eba2586cde39"
down_revision: str | Sequence[str] | None = "e48c26e96f18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cv_experiences",
        sa.Column("cv_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("source_experience_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("position_title", sa.Text(), nullable=False),
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
            name=op.f("ck_cv_experiences_date_order"),
        ),
        sa.CheckConstraint(
            "(start_year IS NULL) = (start_month IS NULL) AND (end_year IS NULL) = (end_month IS NULL)",
            name=op.f("ck_cv_experiences_date_pairs"),
        ),
        sa.CheckConstraint(
            "NOT is_current OR end_year IS NULL",
            name=op.f("ck_cv_experiences_current_without_end"),
        ),
        sa.CheckConstraint(
            "length(trim(company_name)) > 0",
            name=op.f("ck_cv_experiences_company_name_not_blank"),
        ),
        sa.CheckConstraint(
            "length(trim(position_title)) > 0",
            name=op.f("ck_cv_experiences_position_title_not_blank"),
        ),
        sa.CheckConstraint(
            "position > 0", name=op.f("ck_cv_experiences_position_positive")
        ),
        sa.CheckConstraint(
            "start_month BETWEEN 1 AND 12 AND end_month BETWEEN 1 AND 12 AND start_year BETWEEN 1 AND 9999 AND end_year BETWEEN 1 AND 9999",
            name=op.f("ck_cv_experiences_date_ranges"),
        ),
        sa.ForeignKeyConstraint(
            ["cv_id", "user_id"],
            ["cvs.id", "cvs.user_id"],
            name=op.f("fk_cv_experiences_cv_id_cvs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_experience_id", "user_id"],
            ["experiences.id", "experiences.user_id"],
            name=op.f("fk_cv_experiences_source_experience_id_experiences"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cv_experiences")),
        sa.UniqueConstraint(
            "cv_id", "position", name=op.f("uq_cv_experiences_cv_id_position")
        ),
        sa.UniqueConstraint(
            "cv_id",
            "source_experience_id",
            name=op.f("uq_cv_experiences_cv_id_source_experience_id"),
        ),
        sa.UniqueConstraint(
            "id",
            "source_experience_id",
            name=op.f("uq_cv_experiences_id_source_experience_id"),
        ),
    )
    op.create_index(
        "ix_cv_experiences_source_owner",
        "cv_experiences",
        ["source_experience_id", "user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cv_experiences_source_owner", table_name="cv_experiences")
    op.drop_table("cv_experiences")
