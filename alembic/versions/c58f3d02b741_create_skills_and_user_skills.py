"""
Create the empty skill catalog and user skill links.

Revision ID: c58f3d02b741
Revises: b47e2c91a630
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c58f3d02b741"
down_revision: str | Sequence[str] | None = "b47e2c91a630"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("skill_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("skill_name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("skill_id", name=op.f("pk_skills")),
        sa.CheckConstraint(
            "length(trim(skill_name)) > 0", name=op.f("ck_skills_skill_name_not_blank")
        ),
    )
    op.create_index(
        "uq_skills_name_normalized",
        "skills",
        [sa.text("lower(btrim(skill_name))")],
        unique=True,
    )
    op.create_table(
        "user_skills",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("skill_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "skill_id", name=op.f("pk_user_skills")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_skills_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.skill_id"],
            name=op.f("fk_user_skills_skill_id_skills"),
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_user_skills_skill_id", "user_skills", ["skill_id"])


def downgrade() -> None:
    op.drop_table("user_skills")
    op.drop_table("skills")
