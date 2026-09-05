"""enable pgvector extension

Revision ID: f6f205c04f44
Revises:
Create Date: 2026-09-05 16:19:32.185321

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f6f205c04f44"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Must run before any Vector column exists. The pgvector image ships the
    # extension but does not enable it per database.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
