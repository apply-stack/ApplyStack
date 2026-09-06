"""
Add shared timestamp function.

Revision ID: 5e394455d5ad
Revises: c58f3d02b741
"""

from collections.abc import Sequence

from alembic import op

revision: str = "5e394455d5ad"
down_revision: str | Sequence[str] | None = "c58f3d02b741"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION touch_record_timestamps() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            NEW.created_at := OLD.created_at;
            NEW.updated_at := statement_timestamp();
            RETURN NEW;
        END;
        $$
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION touch_record_timestamps()")
