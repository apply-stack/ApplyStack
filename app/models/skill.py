"""Shared technical skill catalog and user assignments."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Index,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (
        CheckConstraint("length(trim(skill_name)) > 0", name="skill_name_not_blank"),
    )

    skill_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    skill_name: Mapped[str] = mapped_column(Text)


Index(
    "uq_skills_name_normalized", func.lower(func.btrim(Skill.skill_name)), unique=True
)


class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (Index("ix_user_skills_skill_id", "skill_id"),)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skills.skill_id", ondelete="RESTRICT"), primary_key=True
    )
