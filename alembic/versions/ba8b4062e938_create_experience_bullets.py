"""
Create experience bullets.

Revision ID: ba8b4062e938
Revises: ea8d6ad64b3b
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "ba8b4062e938"
down_revision: str | Sequence[str] | None = "ea8d6ad64b3b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experience_bullets",
        sa.Column("experience_id", sa.BigInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(content)) > 0",
            name=op.f("ck_experience_bullets_content_not_blank"),
        ),
        sa.CheckConstraint(
            "position > 0", name=op.f("ck_experience_bullets_position_positive")
        ),
        sa.ForeignKeyConstraint(
            ["experience_id"],
            ["experiences.id"],
            name=op.f("fk_experience_bullets_experience_id_experiences"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_experience_bullets")),
        sa.UniqueConstraint(
            "experience_id",
            "position",
            name=op.f("uq_experience_bullets_experience_id_position"),
        ),
        sa.UniqueConstraint(
            "id", "experience_id", name=op.f("uq_experience_bullets_id_experience_id")
        ),
    )
    op.execute(
        "CREATE TRIGGER touch_timestamps BEFORE UPDATE ON experience_bullets FOR EACH ROW EXECUTE FUNCTION touch_record_timestamps()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER touch_timestamps ON experience_bullets")
    op.drop_table("experience_bullets")
