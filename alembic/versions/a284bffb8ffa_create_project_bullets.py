"""
Create project bullets.

Revision ID: a284bffb8ffa
Revises: 843a86b2bda2
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a284bffb8ffa"
down_revision: str | Sequence[str] | None = "843a86b2bda2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_bullets",
        sa.Column("project_id", sa.BigInteger(), nullable=False),
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
            name=op.f("ck_project_bullets_content_not_blank"),
        ),
        sa.CheckConstraint(
            "position > 0", name=op.f("ck_project_bullets_position_positive")
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_project_bullets_project_id_projects"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_bullets")),
        sa.UniqueConstraint(
            "id", "project_id", name=op.f("uq_project_bullets_id_project_id")
        ),
        sa.UniqueConstraint(
            "project_id",
            "position",
            name=op.f("uq_project_bullets_project_id_position"),
        ),
    )
    op.execute(
        "CREATE TRIGGER touch_timestamps BEFORE UPDATE ON project_bullets FOR EACH ROW EXECUTE FUNCTION touch_record_timestamps()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER touch_timestamps ON project_bullets")
    op.drop_table("project_bullets")
