"""
Add user matching version.

Revision ID: 48811ec46a68
Revises: 5e394455d5ad
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "48811ec46a68"
down_revision: str | Sequence[str] | None = "5e394455d5ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "matching_version",
            sa.BigInteger(),
            server_default=sa.text("1"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        op.f("ck_users_matching_version_positive"), "users", "matching_version > 0"
    )
    op.execute("""
        CREATE FUNCTION bump_user_skill_version() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'UPDATE' AND NEW IS NOT DISTINCT FROM OLD THEN
                RETURN NEW;
            END IF;
            IF TG_OP <> 'INSERT' THEN
                UPDATE users SET matching_version = matching_version + 1 WHERE id = OLD.user_id;
            END IF;
            IF TG_OP = 'INSERT' THEN
                UPDATE users SET matching_version = matching_version + 1 WHERE id = NEW.user_id;
            ELSIF TG_OP = 'UPDATE' AND NEW.user_id <> OLD.user_id THEN
                UPDATE users SET matching_version = matching_version + 1 WHERE id = NEW.user_id;
            END IF;
            RETURN NULL;
        END;
        $$
    """)
    op.execute(
        "CREATE TRIGGER user_skill_version AFTER INSERT OR UPDATE OR DELETE ON user_skills FOR EACH ROW EXECUTE FUNCTION bump_user_skill_version()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER user_skill_version ON user_skills")
    op.execute("DROP FUNCTION bump_user_skill_version()")
    op.drop_constraint(
        op.f("ck_users_matching_version_positive"), "users", type_="check"
    )
    op.drop_column("users", "matching_version")
