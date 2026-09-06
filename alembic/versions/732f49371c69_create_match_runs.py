"""
Create match runs.

Revision ID: 732f49371c69
Revises: 08d1efb0019f
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "732f49371c69"
down_revision: str | Sequence[str] | None = "08d1efb0019f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "match_runs",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status", sa.Text(), server_default=sa.text("'running'"), nullable=False
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "heartbeat_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_matching_version", sa.BigInteger(), nullable=False),
        sa.Column("scoring_version", sa.Text(), nullable=False),
        sa.Column(
            "processed_job_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.CheckConstraint(
            "(status = 'running') = (completed_at IS NULL)",
            name=op.f("ck_match_runs_completion_state"),
        ),
        sa.CheckConstraint(
            "status IN ('running', 'completed', 'failed', 'superseded')",
            name=op.f("ck_match_runs_status_allowed"),
        ),
        sa.CheckConstraint(
            "completed_at >= started_at", name=op.f("ck_match_runs_time_order")
        ),
        sa.CheckConstraint(
            "length(trim(scoring_version)) > 0",
            name=op.f("ck_match_runs_scoring_version_not_blank"),
        ),
        sa.CheckConstraint(
            "processed_job_count >= 0 AND user_matching_version > 0",
            name=op.f("ck_match_runs_counts_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_match_runs_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_match_runs")),
        sa.UniqueConstraint(
            "id",
            "user_id",
            "user_matching_version",
            "scoring_version",
            name=op.f("uq_match_runs_id_user_id_user_matching_version_scoring_version"),
        ),
    )
    op.create_index(
        "ix_match_runs_user_started",
        "match_runs",
        ["user_id", "started_at"],
        unique=False,
    )
    op.create_index(
        "uq_match_runs_active_user",
        "match_runs",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'running'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_match_runs_active_user",
        table_name="match_runs",
        postgresql_where=sa.text("status = 'running'"),
    )
    op.drop_index("ix_match_runs_user_started", table_name="match_runs")
    op.drop_table("match_runs")
