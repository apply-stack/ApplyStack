"""
Create match results.

Revision ID: 843a86b2bda2
Revises: ba8b4062e938
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "843a86b2bda2"
down_revision: str | Sequence[str] | None = "ba8b4062e938"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "match_results",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("job_id", sa.BigInteger(), nullable=False),
        sa.Column("percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("user_matching_version", sa.BigInteger(), nullable=False),
        sa.Column("job_matching_version", sa.BigInteger(), nullable=False),
        sa.Column("scoring_version", sa.Text(), nullable=False),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("match_run_id", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "percentage >= 0 AND percentage <= 100",
            name=op.f("ck_match_results_percentage_range"),
        ),
        sa.CheckConstraint(
            "user_matching_version > 0 AND job_matching_version > 0",
            name=op.f("ck_match_results_versions_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            name=op.f("fk_match_results_job_id_jobs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["match_run_id", "user_id", "user_matching_version", "scoring_version"],
            [
                "match_runs.id",
                "match_runs.user_id",
                "match_runs.user_matching_version",
                "match_runs.scoring_version",
            ],
            name=op.f("fk_match_results_match_run_id_match_runs"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_match_results_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("user_id", "job_id", name=op.f("pk_match_results")),
    )
    op.create_index(
        "ix_match_results_job_id", "match_results", ["job_id"], unique=False
    )
    op.create_index(
        "ix_match_results_run", "match_results", ["match_run_id"], unique=False
    )
    op.create_index(
        "ix_match_results_user_score",
        "match_results",
        ["user_id", sa.literal_column("percentage DESC"), "job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_match_results_user_score", table_name="match_results")
    op.drop_index("ix_match_results_run", table_name="match_results")
    op.drop_index("ix_match_results_job_id", table_name="match_results")
    op.drop_table("match_results")
