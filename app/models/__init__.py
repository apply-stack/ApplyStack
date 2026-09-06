"""Imported models so Alembic can discover the complete schema."""

from app.db.base import Base
from app.models.career import (
    Education,
    Experience,
    ExperienceBullet,
    Project,
    ProjectBullet,
    ProjectSkill,
)
from app.models.cv import (
    CV,
    CVEducation,
    CVExperience,
    CVExperienceBullet,
    CVProject,
    CVProjectBullet,
    CVSkill,
)
from app.models.job import Job, JobSkill
from app.models.matching import MatchResult, MatchRun, MatchState
from app.models.skill import Skill, UserSkill
from app.models.user import User, UserStatus
from app.models.user_profile import UserProfile

__all__ = [
    "Base",
    "CV",
    "CVEducation",
    "CVExperience",
    "CVExperienceBullet",
    "CVProject",
    "CVProjectBullet",
    "CVSkill",
    "Education",
    "Experience",
    "ExperienceBullet",
    "Job",
    "JobSkill",
    "MatchResult",
    "MatchRun",
    "MatchState",
    "Project",
    "ProjectBullet",
    "ProjectSkill",
    "Skill",
    "User",
    "UserProfile",
    "UserSkill",
    "UserStatus",
]
