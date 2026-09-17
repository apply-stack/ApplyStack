"""Populate the database with a small, realistic fixture set.

    docker compose exec api python -m scripts.seed
    docker compose exec api python -m scripts.seed --reset

Deterministic: the same command always produces the same rows on every
machine, so scores and test assertions stay comparable between developers.

Skills are looked up by name, never by id - the catalog migration assigns
different skill_id values on different databases.
"""

from __future__ import annotations

import argparse
import asyncio
import random
from dataclasses import dataclass, field
from datetime import UTC, date, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.models import (
    CV,
    CVEducation,
    CVExperience,
    CVExperienceBullet,
    CVProject,
    CVProjectBullet,
    CVSkill,
    Education,
    Experience,
    ExperienceBullet,
    Job,
    JobSkill,
    MatchResult,
    MatchRun,
    MatchState,
    Project,
    ProjectBullet,
    ProjectSkill,
    Skill,
    User,
    UserProfile,
    UserSkill,
)

RANDOM_SEED = 1337
TODAY = date(2026, 9, 6)


# --------------------------------------------------------------------------
# Companies.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Company:
    name: str
    boilerplate: str
    sources: tuple[str, ...]


COMPANIES: tuple[Company, ...] = (
    Company(
        "Getir",
        "Getir is the pioneer of ultrafast grocery delivery. Founded in 2015, we "
        "operate in multiple countries and serve millions of customers every "
        "month. Our engineering teams build the systems behind that promise.",
        ("linkedin", "company_site"),
    ),
    Company(
        "Trendyol",
        "Trendyol is one of the largest e-commerce platforms in the region, "
        "connecting millions of buyers with hundreds of thousands of sellers. "
        "We are a technology company at heart.",
        ("linkedin", "kariyer_net"),
    ),
    Company(
        "Peak Games",
        "Peak builds casual mobile games played by tens of millions of people "
        "worldwide. We are a small team with an unusually high bar for craft.",
        ("linkedin", "company_site"),
    ),
    Company(
        "Insider",
        "Insider is a growth management platform helping digital marketers "
        "drive growth across the funnel. We operate in more than 25 countries.",
        ("linkedin", "youthall"),
    ),
    Company(
        "Papara",
        "Papara is a fintech company offering fast, transparent and accessible "
        "financial services. We process millions of transactions every day.",
        ("linkedin", "kariyer_net"),
    ),
    Company(
        "Hepsiburada",
        "Hepsiburada is a leading e-commerce platform. Our technology teams own "
        "everything from the storefront to the logistics network behind it.",
        ("kariyer_net", "company_site"),
    ),
    Company(
        "Dream Games",
        "Dream Games develops high quality mobile puzzle games. We believe small "
        "teams of exceptional people build the best products.",
        ("linkedin",),
    ),
    Company(
        "Aselsan",
        "ASELSAN designs and manufactures advanced defence and communication "
        "systems. Our engineers work on projects with real national impact.",
        ("kariyer_net", "company_site"),
    ),
    Company(
        "Turkcell",
        "Turkcell is a leading digital operator serving tens of millions of "
        "subscribers with converged telecom and digital services.",
        ("kariyer_net", "youthall"),
    ),
    Company(
        "Yemeksepeti",
        "Yemeksepeti is the country's leading online food ordering platform, "
        "part of a global delivery group operating in dozens of markets.",
        ("linkedin", "youthall"),
    ),
    Company(
        "GitLab",
        "GitLab is an all-remote company building the DevSecOps platform. Our "
        "handbook is public and our team spans more than 65 countries.",
        ("greenhouse", "company_site"),
    ),
    Company(
        "Canonical",
        "Canonical is the publisher of Ubuntu, the platform behind most public "
        "cloud workloads. We have been a remote-first company since 2004.",
        ("greenhouse",),
    ),
    Company(
        "Elastic",
        "Elastic is a distributed company building search-powered solutions. "
        "Our source code is open and our teams work from everywhere.",
        ("greenhouse", "company_site"),
    ),
    Company(
        "Datadog",
        "Datadog is the observability platform for cloud applications, bringing "
        "together metrics, traces and logs from across the stack.",
        ("greenhouse",),
    ),
)


# --------------------------------------------------------------------------
# Role templates. Skills reference the seeded catalog by exact name.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Role:
    title: str
    body: str
    required: tuple[str, ...]
    optional: tuple[str, ...]
    employment_type: str
    work_mode: str


ROLES: tuple[Role, ...] = (
    Role(
        "Backend Engineering Intern",
        "You will work alongside our backend engineers on the services that "
        "power our core product. Expect to own a small feature end to end, from "
        "the database schema through the API to the tests that keep it honest. "
        "We will pair with you regularly and review every change you ship.",
        ("Python", "SQL", "PostgreSQL", "REST APIs"),
        ("Docker", "FastAPI", "Redis", "Git"),
        "internship",
        "hybrid",
    ),
    Role(
        "Frontend Engineering Intern",
        "Join the team responsible for the interfaces our customers use every "
        "day. You will build components, improve page performance and help us "
        "keep the design system consistent across a large application.",
        ("JavaScript", "TypeScript", "React", "HTML", "CSS"),
        ("Next.js", "Tailwind CSS", "Vite", "Web Accessibility"),
        "internship",
        "hybrid",
    ),
    Role(
        "Machine Learning Intern",
        "Our applied science team turns product problems into models that ship. "
        "You will help with data preparation, run experiments, and work with "
        "engineers to get a model from a notebook into production.",
        ("Python", "Machine Learning", "PyTorch", "NumPy", "pandas"),
        ("scikit-learn", "Deep Learning", "MLOps", "Jupyter Notebook"),
        "internship",
        "onsite",
    ),
    Role(
        "Data Engineering Intern",
        "You will help build and maintain the pipelines that move data from our "
        "production systems into the warehouse, and the models analysts build "
        "on top of them. Reliability matters more than cleverness here.",
        ("Python", "SQL", "ETL", "Apache Airflow"),
        ("dbt", "Apache Spark", "Data Modeling", "AWS"),
        "internship",
        "hybrid",
    ),
    Role(
        "Mobile Engineering Intern",
        "Work on the application in the hands of millions of users. You will "
        "implement screens, fix real bugs reported by real people, and learn how "
        "a large mobile codebase is kept releasable every single week.",
        ("Kotlin", "Android Development", "Git"),
        ("Jetpack Compose", "REST APIs", "Unit Testing"),
        "internship",
        "onsite",
    ),
    Role(
        "iOS Engineering Intern",
        "Join the iOS team and contribute to features used daily at scale. You "
        "will write Swift, review designs with product, and take part in the "
        "release process from the first day.",
        ("Swift", "iOS Development", "Git"),
        ("SwiftUI", "UIKit", "Unit Testing"),
        "internship",
        "onsite",
    ),
    Role(
        "Platform Engineering Intern",
        "Our platform team owns the tooling every other engineer depends on. "
        "You will work on build pipelines, container images and the internal "
        "developer experience that makes shipping safe and boring.",
        ("Linux", "Docker", "CI/CD", "Bash"),
        ("Kubernetes", "Terraform", "GitHub Actions", "Monitoring"),
        "internship",
        "remote",
    ),
    Role(
        "QA Automation Intern",
        "You will grow our automated test coverage across web and API layers, "
        "investigate flaky tests, and help the team trust its own pipeline "
        "again. Curiosity about how things break is the main requirement.",
        ("Python", "Test Automation", "Unit Testing"),
        ("Playwright", "Selenium", "pytest", "CI/CD"),
        "internship",
        "hybrid",
    ),
    Role(
        "Game Developer Intern",
        "Work with our game teams on live titles played by millions. You will "
        "prototype mechanics, profile performance on real devices and see your "
        "changes reach players within weeks.",
        ("C#", "Unity", "Game Development"),
        ("Game Physics", "Profiling", "Computer Graphics"),
        "internship",
        "onsite",
    ),
    Role(
        "Cybersecurity Intern",
        "Join the security team and help us find problems before anyone else "
        "does. You will assist with reviews, write tooling to automate checks, "
        "and document findings for the engineering teams that fix them.",
        ("Application Security", "Linux", "Python"),
        ("Penetration Testing", "OWASP Top 10", "Network Security"),
        "internship",
        "hybrid",
    ),
    Role(
        "Working Student, Backend",
        "A part-time position for students who can commit around twenty hours a "
        "week during term. You will join a product team and take on scoped "
        "backend tasks with a dedicated mentor.",
        ("Python", "SQL", "Git"),
        ("Django", "PostgreSQL", "Docker"),
        "part_time",
        "hybrid",
    ),
    Role(
        "Junior Software Engineer",
        "A full time role for recent graduates. You will join an established "
        "team, ship production code in your first weeks, and grow through code "
        "review and regular one to one mentoring.",
        ("Java", "SQL", "Data Structures", "Algorithms"),
        ("Spring Boot", "PostgreSQL", "Docker", "REST APIs"),
        "full_time",
        "hybrid",
    ),
    Role(
        "Computer Vision Research Intern",
        "Work with our research group on perception problems. You will read "
        "recent literature, reproduce baselines, and run experiments on our "
        "internal datasets and hardware.",
        ("Python", "Computer Vision", "PyTorch", "OpenCV"),
        ("Deep Learning", "Convolutional Neural Networks", "Linear Algebra"),
        "internship",
        "onsite",
    ),
    Role(
        "Site Reliability Engineering Intern",
        "You will help keep our systems up, working on dashboards, alerts and "
        "runbooks. You will take part in incident reviews and see how a large "
        "production system actually behaves under load.",
        ("Linux", "Monitoring", "Bash"),
        ("Prometheus", "Grafana", "Kubernetes", "Observability"),
        "internship",
        "remote",
    ),
)

APPLICATION_FOOTER = (
    "\n\nTo apply, submit your CV through the link below. We review every "
    "application and aim to respond within two weeks. We are an equal "
    "opportunity employer and welcome applicants from every background."
)


@dataclass
class SeedCounts:
    tables: dict[str, int] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
async def load_skill_ids(session: AsyncSession) -> dict[str, int]:
    rows = (await session.execute(select(Skill.skill_name, Skill.skill_id))).all()
    return dict(rows)  # type: ignore[arg-type]


async def clear_fixtures(session: AsyncSession) -> None:
    """Delete fixture rows in reverse dependency order.

    `skills` is intentionally untouched - that catalog belongs to a migration,
    not to this script.
    """
    for model in (
        CVProjectBullet,
        CVExperienceBullet,
        CVSkill,
        CVProject,
        CVExperience,
        CVEducation,
        CV,
        MatchResult,
        MatchRun,
        MatchState,
        ProjectSkill,
        ProjectBullet,
        ExperienceBullet,
        Project,
        Experience,
        Education,
        UserSkill,
        JobSkill,
        Job,
        UserProfile,
        User,
    ):
        await session.execute(delete(model))
    await session.flush()


def build_description(company: Company, role: Role) -> str:
    return f"{company.boilerplate}\n\n{role.body}{APPLICATION_FOOTER}"


# --------------------------------------------------------------------------
# Jobs
# --------------------------------------------------------------------------
async def seed_jobs(
    session: AsyncSession, skill_ids: dict[str, int], rng: random.Random
) -> list[Job]:
    jobs: list[Job] = []
    counter = 0

    for company in COMPANIES:
        for role in rng.sample(ROLES, k=3):
            counter += 1
            source = rng.choice(company.sources)
            start = TODAY.replace(day=1)
            posted_offset = rng.randint(1, 60)
            start_date = date.fromordinal(start.toordinal() - posted_offset)
            end_date = date.fromordinal(start_date.toordinal() + rng.randint(21, 75))

            # A minority are closed or still awaiting skill extraction, so
            # queries that filter on those columns have something to filter.
            closed = rng.random() < 0.18
            extracted = rng.random() < 0.85

            job = Job(
                job_title=role.title,
                company_name=company.name,
                job_description=build_description(company, role),
                application_url=(
                    f"https://jobs.example.com/{company.name.lower().replace(' ', '-')}"
                    f"/{counter}"
                ),
                application_start_date=start_date,
                application_end_date=end_date,
                location="Remote" if role.work_mode == "remote" else "Istanbul, Turkey",
                work_mode=role.work_mode,
                employment_type=role.employment_type,
                source=source,
                source_job_id=f"{source[:2].upper()}-{counter:04d}",
                status="closed" if closed else "open",
                last_seen_at=datetime.now(UTC),
                skill_extraction_status="completed" if extracted else "pending",
            )
            session.add(job)
            jobs.append(job)

    await session.flush()

    roles_by_title = {role.title: role for role in ROLES}
    for job in jobs:
        if job.skill_extraction_status != "completed":
            continue
        role = roles_by_title[job.job_title]
        for name in role.required:
            session.add(
                JobSkill(job_id=job.id, skill_id=skill_ids[name], is_required=True)
            )
        for name in role.optional:
            session.add(
                JobSkill(job_id=job.id, skill_id=skill_ids[name], is_required=False)
            )
    await session.flush()
    return jobs


# --------------------------------------------------------------------------
# Users and their career content
# --------------------------------------------------------------------------
# Placeholder Argon2id encoding. Real hashes come from app.core.security; this
# only has to satisfy the not-blank constraint.
FIXTURE_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$c2VlZHNlZWRzZWVkc2VlZA$"
    "R0hYc2VlZHNlZWRzZWVkc2VlZHNlZWRzZWVkc2VlZA"
)

USER_SKILLS = (
    "Python",
    "JavaScript",
    "TypeScript",
    "SQL",
    "PostgreSQL",
    "FastAPI",
    "React",
    "Docker",
    "Git",
    "REST APIs",
    "Linux",
    "Data Structures",
    "Algorithms",
    "Unit Testing",
    "pytest",
    "Machine Learning",
    "pandas",
    "NumPy",
)


async def seed_primary_user(
    session: AsyncSession, skill_ids: dict[str, int]
) -> tuple[User, list[Project], Experience, Education]:
    user = User(
        email="deniz.yilmaz@example.com",
        password_hash=FIXTURE_PASSWORD_HASH,
        status="active",
        email_verified_at=datetime.now(UTC),
    )
    session.add(user)
    await session.flush()

    session.add(
        UserProfile(
            user_id=user.id,
            name="Deniz",
            surname="Yilmaz",
            headline="Computer Engineering student, backend and data",
            summary=(
                "Third year Computer Engineering student. Comfortable with "
                "Python and PostgreSQL, currently learning distributed systems. "
                "Looking for a summer internship in backend or data engineering."
            ),
            phone_number="+90 555 000 0000",
            city="Istanbul",
            country_code="TR",
            linkedin_url="https://www.linkedin.com/in/deniz-yilmaz-example",
            github_url="https://github.com/deniz-yilmaz-example",
            website_url="https://deniz-example.dev",
            contact_email="deniz.yilmaz.contact@example.com",
        )
    )

    for name in USER_SKILLS:
        session.add(UserSkill(user_id=user.id, skill_id=skill_ids[name]))

    education = Education(
        user_id=user.id,
        institution_name="Bogazici University",
        degree="Bachelor of Science",
        field_of_study="Computer Engineering",
        location="Istanbul, Turkey",
        start_year=2023,
        start_month=9,
        is_current=True,
    )
    session.add(education)

    experience = Experience(
        user_id=user.id,
        company_name="Kodluyoruz",
        position_title="Backend Development Intern",
        location="Remote",
        start_year=2025,
        start_month=6,
        end_year=2025,
        end_month=9,
        is_current=False,
    )
    session.add(experience)
    await session.flush()

    for position, content in enumerate(
        (
            "Built three REST endpoints in FastAPI backed by PostgreSQL, "
            "covering the full request lifecycle including validation and tests.",
            "Reduced a nightly reporting query from 40 seconds to under 2 by "
            "adding a composite index and rewriting a correlated subquery.",
            "Wrote the integration test suite for the billing module, taking "
            "coverage of that package from 12 percent to 78 percent.",
        ),
        start=1,
    ):
        session.add(
            ExperienceBullet(
                experience_id=experience.id, content=content, position=position
            )
        )

    projects_spec = (
        (
            "ApplyStack",
            "https://applystack.example.dev",
            "https://github.com/deniz-yilmaz-example/applystack",
            (2026, 2),
            None,
            True,
            (
                "Designed a 22 table PostgreSQL schema with database level "
                "constraints and trigger maintained versioning for cache "
                "invalidation.",
                "Built an async FastAPI service with SQLAlchemy 2.0 and Alembic "
                "migrations, containerised with Docker Compose.",
            ),
            ("Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Docker", "Alembic"),
        ),
        (
            "Course Scheduler",
            None,
            "https://github.com/deniz-yilmaz-example/course-scheduler",
            (2025, 3),
            (2025, 5),
            False,
            (
                "Implemented a constraint solver that generates conflict free "
                "timetables for 400 courses in under one second.",
                "Exposed the solver through a React interface used by roughly "
                "150 students during registration week.",
            ),
            ("Python", "Algorithms", "React", "TypeScript"),
        ),
        (
            "Sentiment Analysis for Turkish Reviews",
            None,
            "https://github.com/deniz-yilmaz-example/tr-sentiment",
            (2024, 10),
            (2024, 12),
            False,
            (
                "Fine tuned a multilingual transformer on 30 thousand labelled "
                "Turkish product reviews, reaching 0.89 macro F1.",
                "Compared the result against a TF-IDF baseline and documented "
                "where the extra complexity did and did not pay off.",
            ),
            ("Python", "Machine Learning", "PyTorch", "pandas", "NumPy"),
        ),
    )

    projects: list[Project] = []
    for (
        name,
        url,
        repo,
        (start_year, start_month),
        end,
        current,
        bullets,
        skills,
    ) in projects_spec:
        project = Project(
            user_id=user.id,
            project_name=name,
            project_url=url,
            repository_url=repo,
            start_year=start_year,
            start_month=start_month,
            end_year=end[0] if end else None,
            end_month=end[1] if end else None,
            is_current=current,
        )
        session.add(project)
        await session.flush()
        for position, content in enumerate(bullets, start=1):
            session.add(
                ProjectBullet(project_id=project.id, content=content, position=position)
            )
        for skill_name in skills:
            session.add(
                ProjectSkill(project_id=project.id, skill_id=skill_ids[skill_name])
            )
        projects.append(project)

    await session.flush()
    return user, projects, experience, education


async def seed_secondary_user(session: AsyncSession, skill_ids: dict[str, int]) -> User:
    """A second, thinner user - enough to prove queries are user scoped."""
    user = User(
        email="ada.kaya@example.com",
        password_hash=FIXTURE_PASSWORD_HASH,
        status="pending_verification",
    )
    session.add(user)
    await session.flush()
    session.add(
        UserProfile(
            user_id=user.id,
            name="Ada",
            surname="Kaya",
            headline="Frontend focused CS student",
            city="Ankara",
            country_code="TR",
        )
    )
    for name in ("JavaScript", "TypeScript", "React", "HTML", "CSS", "Git"):
        session.add(UserSkill(user_id=user.id, skill_id=skill_ids[name]))
    await session.flush()
    return user


# --------------------------------------------------------------------------
# One CV, exercising the whole snapshot chain
# --------------------------------------------------------------------------
async def seed_cv(
    session: AsyncSession,
    user: User,
    education: Education,
    experience: Experience,
    projects: list[Project],
    target_job: Job,
    skill_ids: dict[str, int],
) -> CV:
    cv = CV(
        user_id=user.id,
        target_job_id=target_job.id,
        title=f"{target_job.company_name} - {target_job.job_title}",
        language_code="en",
        status="ready",
        template_version="single-column-v1",
        header_snapshot={
            "name": "Deniz Yilmaz",
            "email": "deniz.yilmaz.contact@example.com",
            "phone": "+90 555 000 0000",
            "city": "Istanbul",
            "links": {
                "github": "https://github.com/deniz-yilmaz-example",
                "linkedin": "https://www.linkedin.com/in/deniz-yilmaz-example",
            },
        },
        pdf_storage_key=None,
    )
    session.add(cv)
    await session.flush()

    session.add(
        CVEducation(
            cv_id=cv.id,
            user_id=user.id,
            source_education_id=education.id,
            position=1,
            institution_name=education.institution_name,
            degree=education.degree,
            field_of_study=education.field_of_study,
            location=education.location,
            start_year=education.start_year,
            start_month=education.start_month,
            is_current=education.is_current,
        )
    )

    cv_experience = CVExperience(
        cv_id=cv.id,
        user_id=user.id,
        source_experience_id=experience.id,
        position=1,
        company_name=experience.company_name,
        position_title=experience.position_title,
        location=experience.location,
        start_year=experience.start_year,
        start_month=experience.start_month,
        end_year=experience.end_year,
        end_month=experience.end_month,
        is_current=experience.is_current,
    )
    session.add(cv_experience)
    await session.flush()

    source_bullets = (
        (
            await session.execute(
                select(ExperienceBullet)
                .where(ExperienceBullet.experience_id == experience.id)
                .order_by(ExperienceBullet.position)
            )
        )
        .scalars()
        .all()
    )

    # Only the two bullets relevant to a backend role are carried over. This is
    # the whole point of the snapshot: the CV holds a selection, not a mirror.
    for position, bullet in enumerate(source_bullets[:2], start=1):
        session.add(
            CVExperienceBullet(
                cv_experience_id=cv_experience.id,
                source_experience_id=experience.id,
                source_bullet_id=bullet.id,
                content=bullet.content,
                position=position,
            )
        )

    for position, project in enumerate(projects[:2], start=1):
        cv_project = CVProject(
            cv_id=cv.id,
            user_id=user.id,
            source_project_id=project.id,
            position=position,
            project_name=project.project_name,
            project_url=project.project_url,
            repository_url=project.repository_url,
            start_year=project.start_year,
            start_month=project.start_month,
            end_year=project.end_year,
            end_month=project.end_month,
            is_current=project.is_current,
        )
        session.add(cv_project)
        await session.flush()

        project_bullets = (
            (
                await session.execute(
                    select(ProjectBullet)
                    .where(ProjectBullet.project_id == project.id)
                    .order_by(ProjectBullet.position)
                )
            )
            .scalars()
            .all()
        )
        for bullet_position, bullet in enumerate(project_bullets, start=1):
            session.add(
                CVProjectBullet(
                    cv_project_id=cv_project.id,
                    source_project_id=project.id,
                    source_bullet_id=bullet.id,
                    content=bullet.content,
                    position=bullet_position,
                )
            )

    cv_skills = {
        "languages": ("Python", "TypeScript", "SQL"),
        "frameworks": ("FastAPI", "React"),
        "developer_tools": ("Docker", "Git", "PostgreSQL"),
        "libraries": ("pandas", "NumPy"),
    }
    for category, names in cv_skills.items():
        for position, name in enumerate(names, start=1):
            session.add(
                CVSkill(
                    cv_id=cv.id,
                    skill_id=skill_ids[name],
                    category=category,
                    position=position,
                    display_name=name,
                )
            )

    await session.flush()
    return cv


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
async def run(reset: bool) -> None:
    rng = random.Random(RANDOM_SEED)

    async with AsyncSessionLocal() as session:
        skill_ids = await load_skill_ids(session)
        if not skill_ids:
            raise SystemExit(
                "skills table is empty - run 'alembic upgrade head' first."
            )

        existing = await session.scalar(select(func.count()).select_from(Job))
        if existing and not reset:
            raise SystemExit(
                f"database already holds {existing} jobs. "
                "Re-run with --reset to replace the fixtures."
            )
        if reset:
            await clear_fixtures(session)

        jobs = await seed_jobs(session, skill_ids, rng)
        user, projects, experience, education = await seed_primary_user(
            session, skill_ids
        )
        await seed_secondary_user(session, skill_ids)

        backend_target = next(
            job
            for job in jobs
            if job.job_title == "Backend Engineering Intern" and job.status == "open"
        )
        await seed_cv(
            session, user, education, experience, projects, backend_target, skill_ids
        )

        await session.commit()

    async with AsyncSessionLocal() as session:
        report: list[tuple[str, int]] = []
        for label, model in (
            ("jobs", Job),
            ("job_skills", JobSkill),
            ("users", User),
            ("user_profiles", UserProfile),
            ("user_skills", UserSkill),
            ("educations", Education),
            ("experiences", Experience),
            ("experience_bullets", ExperienceBullet),
            ("projects", Project),
            ("project_bullets", ProjectBullet),
            ("project_skills", ProjectSkill),
            ("cvs", CV),
            ("cv_educations", CVEducation),
            ("cv_experiences", CVExperience),
            ("cv_experience_bullets", CVExperienceBullet),
            ("cv_projects", CVProject),
            ("cv_project_bullets", CVProjectBullet),
            ("cv_skills", CVSkill),
        ):
            count = await session.scalar(select(func.count()).select_from(model))
            report.append((label, count or 0))

    width = max(len(label) for label, _ in report)
    for label, count in report:
        print(f"  {label:<{width}}  {count}")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed fixture data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing fixture rows before seeding (leaves skills alone).",
    )
    args = parser.parse_args()
    asyncio.run(run(args.reset))


if __name__ == "__main__":
    main()
