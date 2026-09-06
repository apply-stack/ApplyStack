"""
Create project skills.

Revision ID: b0f94dc1027e
Revises: a284bffb8ffa
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b0f94dc1027e"
down_revision: str | Sequence[str] | None = "a284bffb8ffa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_skills",
        sa.Column("project_id", sa.BigInteger(), nullable=False),
        sa.Column("skill_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_project_skills_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.skill_id"],
            name=op.f("fk_project_skills_skill_id_skills"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "project_id", "skill_id", name=op.f("pk_project_skills")
        ),
    )
    op.create_index(
        "ix_project_skills_skill_id", "project_skills", ["skill_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_project_skills_skill_id", table_name="project_skills")
    op.drop_table("project_skills")
