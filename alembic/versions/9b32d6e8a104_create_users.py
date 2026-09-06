"""
Create users with verified account states and case-insensitive emails.

Revision ID: 9b32d6e8a104
Revises: f6f205c04f44
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "9b32d6e8a104"
down_revision: str | Sequence[str] | None = "f6f205c04f44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            server_default=sa.text("'pending_verification'"),
            nullable=False,
        ),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.CheckConstraint(
            "status IN ('pending_verification', 'active', 'suspended', 'deactivated')",
            name=op.f("ck_users_status_allowed"),
        ),
        sa.CheckConstraint(
            "status <> 'active' OR email_verified_at IS NOT NULL",
            name=op.f("ck_users_active_requires_verified_email"),
        ),
        sa.CheckConstraint(
            "length(trim(email)) > 0", name=op.f("ck_users_email_not_blank")
        ),
        sa.CheckConstraint(
            "length(trim(password_hash)) > 0",
            name=op.f("ck_users_password_hash_not_blank"),
        ),
    )
    op.create_index(
        "uq_users_email_normalized",
        "users",
        [sa.text("lower(btrim(email))")],
        unique=True,
    )
    # A database trigger also covers updates made outside SQLAlchemy.
    op.execute("""
        CREATE FUNCTION users_set_updated_at() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            NEW.created_at := OLD.created_at;
            NEW.updated_at := statement_timestamp();
            RETURN NEW;
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER users_set_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION users_set_updated_at()
    """)


def downgrade() -> None:
    op.drop_table("users")
    op.execute("DROP FUNCTION users_set_updated_at()")
