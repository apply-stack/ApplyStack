"""
Create cv experience bullets.

Revision ID: 9a4e4b66c7ac
Revises: b0f94dc1027e
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "9a4e4b66c7ac"
down_revision: str | Sequence[str] | None = "b0f94dc1027e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cv_experience_bullets",
        sa.Column("cv_experience_id", sa.BigInteger(), nullable=False),
        sa.Column("source_experience_id", sa.BigInteger(), nullable=False),
        sa.Column("source_bullet_id", sa.BigInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.CheckConstraint(
            "length(trim(content)) > 0",
            name=op.f("ck_cv_experience_bullets_content_not_blank"),
        ),
        sa.CheckConstraint(
            "position > 0", name=op.f("ck_cv_experience_bullets_position_positive")
        ),
        sa.ForeignKeyConstraint(
            ["cv_experience_id", "source_experience_id"],
            ["cv_experiences.id", "cv_experiences.source_experience_id"],
            name=op.f("fk_cv_experience_bullets_cv_experience_id_cv_experiences"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_bullet_id", "source_experience_id"],
            ["experience_bullets.id", "experience_bullets.experience_id"],
            name=op.f("fk_cv_experience_bullets_source_bullet_id_experience_bullets"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cv_experience_bullets")),
        sa.UniqueConstraint(
            "cv_experience_id",
            "position",
            name=op.f("uq_cv_experience_bullets_cv_experience_id_position"),
        ),
        sa.UniqueConstraint(
            "cv_experience_id",
            "source_bullet_id",
            name=op.f("uq_cv_experience_bullets_cv_experience_id_source_bullet_id"),
        ),
    )
    op.create_index(
        "ix_cv_experience_bullets_source",
        "cv_experience_bullets",
        ["source_bullet_id", "source_experience_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cv_experience_bullets_source", table_name="cv_experience_bullets")
    op.drop_table("cv_experience_bullets")
