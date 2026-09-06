"""
Create experiences.

Revision ID: f3260588c3b2
Revises: f25afffa4306
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f3260588c3b2"
down_revision: str | Sequence[str] | None = "f25afffa4306"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiences",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("position_title", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
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
            name=op.f("ck_experiences_date_order"),
        ),
        sa.CheckConstraint(
            "(start_year IS NULL) = (start_month IS NULL) AND (end_year IS NULL) = (end_month IS NULL)",
            name=op.f("ck_experiences_date_pairs"),
        ),
        sa.CheckConstraint(
            "NOT is_current OR end_year IS NULL",
            name=op.f("ck_experiences_current_without_end"),
        ),
        sa.CheckConstraint(
            "length(trim(company_name)) > 0",
            name=op.f("ck_experiences_company_name_not_blank"),
        ),
        sa.CheckConstraint(
            "length(trim(position_title)) > 0",
            name=op.f("ck_experiences_position_title_not_blank"),
        ),
        sa.CheckConstraint(
            "start_month BETWEEN 1 AND 12 AND end_month BETWEEN 1 AND 12 AND start_year BETWEEN 1 AND 9999 AND end_year BETWEEN 1 AND 9999",
            name=op.f("ck_experiences_date_ranges"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_experiences_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_experiences")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_experiences_id_user_id")),
    )
    op.create_index("ix_experiences_user_id", "experiences", ["user_id"], unique=False)
    op.execute(
        "CREATE TRIGGER touch_timestamps BEFORE UPDATE ON experiences FOR EACH ROW EXECUTE FUNCTION touch_record_timestamps()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER touch_timestamps ON experiences")
    op.drop_index("ix_experiences_user_id", table_name="experiences")
    op.drop_table("experiences")
