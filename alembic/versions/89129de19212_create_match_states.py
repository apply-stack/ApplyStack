"""
Create match states.

Revision ID: 89129de19212
Revises: 732f49371c69
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "89129de19212"
down_revision: str | Sequence[str] | None = "732f49371c69"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "match_states",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("last_successful_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_completed_user_version", sa.BigInteger(), nullable=True),
        sa.Column("last_completed_scoring_version", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "last_completed_user_version > 0",
            name=op.f("ck_match_states_version_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_match_states_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_match_states")),
    )


def downgrade() -> None:
    op.drop_table("match_states")
