"""
Create jobs.

Revision ID: d5b0b171d5ba
Revises: 48811ec46a68
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d5b0b171d5ba"
down_revision: str | Sequence[str] | None = "48811ec46a68"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("job_title", sa.Text(), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("application_url", sa.Text(), nullable=False),
        sa.Column("application_start_date", sa.Date(), nullable=True),
        sa.Column("application_end_date", sa.Date(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("work_mode", sa.Text(), nullable=True),
        sa.Column("employment_type", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_job_id", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.Text(), server_default=sa.text("'unknown'"), nullable=False
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "matching_version",
            sa.BigInteger(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "skill_extraction_status",
            sa.Text(),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
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
            "employment_type IN ('internship', 'full_time', 'part_time', 'contract')",
            name=op.f("ck_jobs_employment_type_allowed"),
        ),
        sa.CheckConstraint(
            "skill_extraction_status IN ('pending', 'completed', 'failed')",
            name=op.f("ck_jobs_extraction_status_allowed"),
        ),
        sa.CheckConstraint(
            "status IN ('open', 'closed', 'unknown')",
            name=op.f("ck_jobs_status_allowed"),
        ),
        sa.CheckConstraint(
            "work_mode IN ('remote', 'hybrid', 'onsite')",
            name=op.f("ck_jobs_work_mode_allowed"),
        ),
        sa.CheckConstraint(
            "application_end_date >= application_start_date",
            name=op.f("ck_jobs_date_order"),
        ),
        sa.CheckConstraint(
            "length(trim(job_title)) > 0 AND length(trim(company_name)) > 0 AND length(trim(job_description)) > 0 AND length(trim(application_url)) > 0 AND length(trim(source)) > 0",
            name=op.f("ck_jobs_required_text"),
        ),
        sa.CheckConstraint(
            "matching_version > 0", name=op.f("ck_jobs_matching_version_positive")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
        sa.UniqueConstraint(
            "source", "source_job_id", name=op.f("uq_jobs_source_source_job_id")
        ),
    )
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"], unique=False)
    op.create_index(
        "ix_jobs_matching_candidates",
        "jobs",
        ["status", "skill_extraction_status", "id"],
        unique=False,
    )
    op.execute("""
        CREATE FUNCTION bump_job_content_version() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF (NEW.job_title, NEW.company_name, NEW.job_description, NEW.location,
                NEW.work_mode, NEW.employment_type, NEW.application_start_date,
                NEW.application_end_date, NEW.status, NEW.skill_extraction_status)
                IS DISTINCT FROM
               (OLD.job_title, OLD.company_name, OLD.job_description, OLD.location,
                OLD.work_mode, OLD.employment_type, OLD.application_start_date,
                OLD.application_end_date, OLD.status, OLD.skill_extraction_status) THEN
                NEW.matching_version := OLD.matching_version + 1;
            END IF;
            IF NEW.job_description IS DISTINCT FROM OLD.job_description THEN
                NEW.skill_extraction_status := 'pending';
            END IF;
            RETURN NEW;
        END;
        $$
    """)
    op.execute(
        "CREATE TRIGGER job_content_version BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION bump_job_content_version()"
    )
    op.execute(
        "CREATE TRIGGER touch_timestamps BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION touch_record_timestamps()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER touch_timestamps ON jobs")
    op.execute("DROP TRIGGER job_content_version ON jobs")
    op.execute("DROP FUNCTION bump_job_content_version()")
    op.drop_index("ix_jobs_matching_candidates", table_name="jobs")
    op.drop_index("ix_jobs_created_at", table_name="jobs")
    op.drop_table("jobs")
