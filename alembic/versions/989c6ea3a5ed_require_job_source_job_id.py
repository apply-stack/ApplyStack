"""require job source_job_id

Revision ID: 989c6ea3a5ed
Revises: ddfebe24bccf
Create Date: 2026-09-17

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "989c6ea3a5ed"
down_revision: str | Sequence[str] | None = "ddfebe24bccf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # LinkedIn always supplies a posting id. A NULL here would make the
    # (source, source_job_id) unique constraint silently ineffective, since
    # NULLs never compare equal - the scraper could insert the same posting
    # every run. Fails loudly if any NULL rows exist, which is the intent.
    op.alter_column("jobs", "source_job_id", existing_type=sa.Text(), nullable=False)
    op.create_check_constraint(
        "source_job_id_not_blank", "jobs", "length(trim(source_job_id)) > 0"
    )


def downgrade() -> None:
    op.drop_constraint("source_job_id_not_blank", "jobs", type_="check")
    op.alter_column("jobs", "source_job_id", existing_type=sa.Text(), nullable=True)
