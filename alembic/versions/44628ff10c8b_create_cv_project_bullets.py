"""
Create cv project bullets.

Revision ID: 44628ff10c8b
Revises: 9a4e4b66c7ac
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "44628ff10c8b"
down_revision: str | Sequence[str] | None = "9a4e4b66c7ac"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cv_project_bullets",
        sa.Column("cv_project_id", sa.BigInteger(), nullable=False),
        sa.Column("source_project_id", sa.BigInteger(), nullable=False),
        sa.Column("source_bullet_id", sa.BigInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.CheckConstraint(
            "length(trim(content)) > 0",
            name=op.f("ck_cv_project_bullets_content_not_blank"),
        ),
        sa.CheckConstraint(
            "position > 0", name=op.f("ck_cv_project_bullets_position_positive")
        ),
        sa.ForeignKeyConstraint(
            ["cv_project_id", "source_project_id"],
            ["cv_projects.id", "cv_projects.source_project_id"],
            name=op.f("fk_cv_project_bullets_cv_project_id_cv_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_bullet_id", "source_project_id"],
            ["project_bullets.id", "project_bullets.project_id"],
            name=op.f("fk_cv_project_bullets_source_bullet_id_project_bullets"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cv_project_bullets")),
        sa.UniqueConstraint(
            "cv_project_id",
            "position",
            name=op.f("uq_cv_project_bullets_cv_project_id_position"),
        ),
        sa.UniqueConstraint(
            "cv_project_id",
            "source_bullet_id",
            name=op.f("uq_cv_project_bullets_cv_project_id_source_bullet_id"),
        ),
    )
    op.create_index(
        "ix_cv_project_bullets_source",
        "cv_project_bullets",
        ["source_bullet_id", "source_project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cv_project_bullets_source", table_name="cv_project_bullets")
    op.drop_table("cv_project_bullets")
