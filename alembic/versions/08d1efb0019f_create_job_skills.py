"""
Create job skills.

Revision ID: 08d1efb0019f
Revises: f3260588c3b2
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "08d1efb0019f"
down_revision: str | Sequence[str] | None = "f3260588c3b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_skills",
        sa.Column("job_id", sa.BigInteger(), nullable=False),
        sa.Column("skill_id", sa.BigInteger(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            name=op.f("fk_job_skills_job_id_jobs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.skill_id"],
            name=op.f("fk_job_skills_skill_id_skills"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("job_id", "skill_id", name=op.f("pk_job_skills")),
    )
    op.create_index("ix_job_skills_skill_id", "job_skills", ["skill_id"], unique=False)
    op.execute("""
        CREATE FUNCTION bump_job_skill_version() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'UPDATE' AND NEW IS NOT DISTINCT FROM OLD THEN
                RETURN NEW;
            END IF;
            IF TG_OP <> 'INSERT' THEN
                UPDATE jobs SET matching_version = matching_version + 1 WHERE id = OLD.job_id;
            END IF;
            IF TG_OP = 'INSERT' THEN
                UPDATE jobs SET matching_version = matching_version + 1 WHERE id = NEW.job_id;
            ELSIF TG_OP = 'UPDATE' AND NEW.job_id <> OLD.job_id THEN
                UPDATE jobs SET matching_version = matching_version + 1 WHERE id = NEW.job_id;
            END IF;
            RETURN NULL;
        END;
        $$
    """)
    op.execute(
        "CREATE TRIGGER job_skill_version AFTER INSERT OR UPDATE OR DELETE ON job_skills FOR EACH ROW EXECUTE FUNCTION bump_job_skill_version()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER job_skill_version ON job_skills")
    op.execute("DROP FUNCTION bump_job_skill_version()")
    op.drop_index("ix_job_skills_skill_id", table_name="job_skills")
    op.drop_table("job_skills")
