"""
Create one-to-one user profiles.

Revision ID: b47e2c91a630
Revises: 9b32d6e8a104
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b47e2c91a630"
down_revision: str | Sequence[str] | None = "9b32d6e8a104"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("surname", sa.Text(), nullable=False),
        sa.Column("headline", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("phone_number", sa.Text(), nullable=True),
        sa.Column("city", sa.Text(), nullable=True),
        sa.Column("country_code", sa.String(2), nullable=True),
        sa.Column("linkedin_url", sa.Text(), nullable=True),
        sa.Column("github_url", sa.Text(), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user_profiles")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_profiles_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0", name=op.f("ck_user_profiles_name_not_blank")
        ),
        sa.CheckConstraint(
            "length(trim(surname)) > 0", name=op.f("ck_user_profiles_surname_not_blank")
        ),
        sa.CheckConstraint(
            "country_code IS NULL OR country_code ~ '^[A-Z]{2}$'",
            name=op.f("ck_user_profiles_country_code_format"),
        ),
        sa.CheckConstraint(
            "contact_email IS NULL OR length(trim(contact_email)) > 0",
            name=op.f("ck_user_profiles_contact_email_not_blank"),
        ),
    )
    op.execute("""
        CREATE FUNCTION user_profiles_set_updated_at() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            NEW.created_at := OLD.created_at;
            NEW.updated_at := statement_timestamp();
            RETURN NEW;
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER user_profiles_set_updated_at
        BEFORE UPDATE ON user_profiles
        FOR EACH ROW EXECUTE FUNCTION user_profiles_set_updated_at()
    """)


def downgrade() -> None:
    op.drop_table("user_profiles")
    op.execute("DROP FUNCTION user_profiles_set_updated_at()")
