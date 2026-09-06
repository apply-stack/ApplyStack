"""
Create projects.

Revision ID: 09df6f5a00c8
Revises: 89129de19212
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "09df6f5a00c8"
down_revision: str | Sequence[str] | None = "89129de19212"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("project_name", sa.Text(), nullable=False),
        sa.Column("project_url", sa.Text(), nullable=True),
        sa.Column("repository_url", sa.Text(), nullable=True),
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
        sa.Column("start_year", sa.Integer(), nullable=True),
        sa.Column("start_month", sa.Integer(), nullable=True),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("end_month", sa.Integer(), nullable=True),
        sa.Column(
            "is_current", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.CheckConstraint(
            "(end_year, end_month) >= (start_year, start_month)",
            name=op.f("ck_projects_date_order"),
        ),
        sa.CheckConstraint(
            "(start_year IS NULL) = (start_month IS NULL) AND (end_year IS NULL) = (end_month IS NULL)",
            name=op.f("ck_projects_date_pairs"),
        ),
        sa.CheckConstraint(
            "NOT is_current OR end_year IS NULL",
            name=op.f("ck_projects_current_without_end"),
        ),
        sa.CheckConstraint(
            "length(trim(project_name)) > 0",
            name=op.f("ck_projects_project_name_not_blank"),
        ),
        sa.CheckConstraint(
            "start_month BETWEEN 1 AND 12 AND end_month BETWEEN 1 AND 12 AND start_year BETWEEN 1 AND 9999 AND end_year BETWEEN 1 AND 9999",
            name=op.f("ck_projects_date_ranges"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_projects_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_projects_id_user_id")),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"], unique=False)
    op.execute(
        "CREATE TRIGGER touch_timestamps BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION touch_record_timestamps()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER touch_timestamps ON projects")
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_table("projects")
