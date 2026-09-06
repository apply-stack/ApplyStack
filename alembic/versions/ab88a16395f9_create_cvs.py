"""
Create cvs.

Revision ID: ab88a16395f9
Revises: d5b0b171d5ba
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "ab88a16395f9"
down_revision: str | Sequence[str] | None = "d5b0b171d5ba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cvs",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("target_job_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("language_code", sa.Text(), nullable=False),
        sa.Column(
            "status", sa.Text(), server_default=sa.text("'draft'"), nullable=False
        ),
        sa.Column("template_version", sa.Text(), nullable=False),
        sa.Column(
            "header_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("pdf_storage_key", sa.Text(), nullable=True),
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
            "jsonb_typeof(header_snapshot) = 'object'",
            name=op.f("ck_cvs_header_object"),
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'generating', 'ready', 'failed')",
            name=op.f("ck_cvs_status_allowed"),
        ),
        sa.CheckConstraint(
            "length(trim(title)) > 0 AND length(trim(language_code)) > 0 AND length(trim(template_version)) > 0",
            name=op.f("ck_cvs_required_text"),
        ),
        sa.ForeignKeyConstraint(
            ["target_job_id"],
            ["jobs.id"],
            name=op.f("fk_cvs_target_job_id_jobs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_cvs_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cvs")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_cvs_id_user_id")),
    )
    op.create_index("ix_cvs_target_job_id", "cvs", ["target_job_id"], unique=False)
    op.create_index("ix_cvs_user_id", "cvs", ["user_id"], unique=False)
    op.execute(
        "CREATE TRIGGER touch_timestamps BEFORE UPDATE ON cvs FOR EACH ROW EXECUTE FUNCTION touch_record_timestamps()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER touch_timestamps ON cvs")
    op.drop_index("ix_cvs_user_id", table_name="cvs")
    op.drop_index("ix_cvs_target_job_id", table_name="cvs")
    op.drop_table("cvs")
