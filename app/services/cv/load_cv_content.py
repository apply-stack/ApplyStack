"""Load stored CV content for subsequent rendering or template conversion."""

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import ProjectSkill
from app.models.cv import (
    CV,
    CVEducation,
    CVExperience,
    CVExperienceBullet,
    CVProject,
    CVProjectBullet,
    CVSkill,
)
from app.models.skill import Skill


class CVNotFoundError(LookupError):
    """The requested CV does not exist."""


@dataclass(frozen=True)
class ExperienceContent:
    record: CVExperience
    bullets: tuple[CVExperienceBullet, ...]


@dataclass(frozen=True)
class ProjectContent:
    record: CVProject
    bullets: tuple[CVProjectBullet, ...]
    skills: tuple[Skill, ...] = ()


@dataclass(frozen=True)
class CVContent:
    """Fully loaded rows, grouped without changing their saved wording or dates.

    These are ORM records, not a resume JSON schema. No lazy relationships are
    needed to read their columns. Consume before expiring the session's records.
    """

    cv: CV
    educations: tuple[CVEducation, ...]
    experiences: tuple[ExperienceContent, ...]
    projects: tuple[ProjectContent, ...]
    skills_by_category: dict[str, tuple[CVSkill, ...]]

    @property
    def header_snapshot(self) -> dict[str, Any]:
        """Return the complete header without sharing mutable nested values."""
        return deepcopy(self.cv.header_snapshot)


async def load_cv_content(session: AsyncSession, cv_id: int) -> CVContent:
    """Read CV snapshots and current project skills, using a fixed number of queries (no N+1).

    The caller owns the session/transaction and must authorize access before
    exposing this internal service to a user. Source profile/career/catalog
    records are not substituted for saved CV snapshots, except project skills:
    these are read live from project_skills and the skills catalog.
    """
    cv = await session.scalar(select(CV).where(CV.id == cv_id))
    if cv is None:
        raise CVNotFoundError(f"CV {cv_id} not found")

    educations = tuple(
        await session.scalars(
            select(CVEducation)
            .where(CVEducation.cv_id == cv_id)
            .order_by(CVEducation.position)
        )
    )
    experiences = await session.scalars(
        select(CVExperience)
        .where(CVExperience.cv_id == cv_id)
        .order_by(CVExperience.position)
    )
    experience_bullets: dict[int, list[CVExperienceBullet]] = defaultdict(list)
    for bullet in await session.scalars(
        select(CVExperienceBullet)
        .join(CVExperience, CVExperience.id == CVExperienceBullet.cv_experience_id)
        .where(CVExperience.cv_id == cv_id)
        .order_by(CVExperienceBullet.position)
    ):
        experience_bullets[bullet.cv_experience_id].append(bullet)

    projects = await session.scalars(
        select(CVProject).where(CVProject.cv_id == cv_id).order_by(CVProject.position)
    )
    project_bullets: dict[int, list[CVProjectBullet]] = defaultdict(list)
    for project_bullet in await session.scalars(
        select(CVProjectBullet)
        .join(CVProject, CVProject.id == CVProjectBullet.cv_project_id)
        .where(CVProject.cv_id == cv_id)
        .order_by(CVProjectBullet.position)
    ):
        project_bullets[project_bullet.cv_project_id].append(project_bullet)

    project_skills: dict[int, list[Skill]] = defaultdict(list)
    for project_id, project_skill in await session.execute(
        select(CVProject.id, Skill)
        .join(ProjectSkill, ProjectSkill.project_id == CVProject.source_project_id)
        .join(Skill, Skill.skill_id == ProjectSkill.skill_id)
        .where(CVProject.cv_id == cv_id)
        .order_by(Skill.skill_name, Skill.skill_id)
    ):
        project_skills[project_id].append(project_skill)

    skills: dict[str, list[CVSkill]] = {
        category: []
        for category in ("languages", "frameworks", "developer_tools", "libraries")
    }
    for skill in await session.scalars(
        select(CVSkill)
        .where(CVSkill.cv_id == cv_id)
        .order_by(CVSkill.category, CVSkill.position)
    ):
        skills[skill.category].append(skill)

    return CVContent(
        cv=cv,
        educations=educations,
        experiences=tuple(
            ExperienceContent(record, tuple(experience_bullets[record.id]))
            for record in experiences
        ),
        projects=tuple(
            ProjectContent(
                record,
                tuple(project_bullets[record.id]),
                tuple(project_skills[record.id]),
            )
            for record in projects
        ),
        skills_by_category={key: tuple(rows) for key, rows in skills.items()},
    )
