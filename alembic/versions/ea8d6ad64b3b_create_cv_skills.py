"""
Create cv skills.

Revision ID: ea8d6ad64b3b
Revises: 72d53060157a
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "ea8d6ad64b3b"
down_revision: str | Sequence[str] | None = "72d53060157a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cv_skills",
        sa.Column("cv_id", sa.BigInteger(), nullable=False),
        sa.Column("skill_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "category IN ('languages', 'frameworks', 'developer_tools', 'libraries')",
            name=op.f("ck_cv_skills_category_allowed"),
        ),
        sa.CheckConstraint(
            "length(trim(display_name)) > 0",
            name=op.f("ck_cv_skills_display_name_not_blank"),
        ),
        sa.CheckConstraint("position > 0", name=op.f("ck_cv_skills_position_positive")),
        sa.ForeignKeyConstraint(
            ["cv_id"],
            ["cvs.id"],
            name=op.f("fk_cv_skills_cv_id_cvs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.skill_id"],
            name=op.f("fk_cv_skills_skill_id_skills"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("cv_id", "skill_id", name=op.f("pk_cv_skills")),
        sa.UniqueConstraint(
            "cv_id",
            "category",
            "position",
            name=op.f("uq_cv_skills_cv_id_category_position"),
        ),
    )
    op.create_index("ix_cv_skills_skill_id", "cv_skills", ["skill_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cv_skills_skill_id", table_name="cv_skills")
    op.drop_table("cv_skills")
