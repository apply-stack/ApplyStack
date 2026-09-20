"""Exercise retrieval SQL against SQLite; PostgreSQL constraints live elsewhere."""

import asyncio
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import JSON, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

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
from app.services.cv import CVNotFoundError, load_cv_content


@pytest.fixture
def database():
    engine = create_engine("sqlite://")
    models = (
        ProjectSkill,
        Skill,
        CV,
        CVEducation,
        CVExperience,
        CVExperienceBullet,
        CVProject,
        CVProjectBullet,
        CVSkill,
    )
    # Only column storage is needed here; do not alter production metadata.
    with engine.begin() as connection:
        for model in models:
            columns = []
            for column in model.__table__.columns:
                column_type = JSON() if isinstance(column.type, JSONB) else column.type
                columns.append(f'"{column.name}" {column_type.compile(engine.dialect)}')
            connection.exec_driver_sql(
                f'CREATE TABLE "{model.__tablename__}" ({", ".join(columns)})'
            )
    with Session(engine) as session:
        yield (
            session,
            AsyncMock(
                execute=AsyncMock(side_effect=session.execute),
                scalar=AsyncMock(side_effect=session.scalar),
                scalars=AsyncMock(side_effect=session.scalars),
            ),
        )
    engine.dispose()


def test_loads_only_requested_snapshot_in_saved_order(database):
    session, reader = database
    session.add_all(
        [
            CV(
                id=1,
                user_id=1,
                title="Saved CV",
                header_snapshot={"name": "Saved name"},
            ),
            CV(id=2, user_id=2, title="Other CV", header_snapshot={}),
        ]
    )
    for cv_id in (1, 2):
        for position in (2, 1):
            row_id = cv_id * 10 + position
            session.add_all(
                [
                    CVEducation(
                        id=row_id,
                        cv_id=cv_id,
                        position=position,
                        institution_name=f"School {position}",
                    ),
                    CVExperience(
                        id=row_id,
                        cv_id=cv_id,
                        position=position,
                        company_name=f"Company {position}",
                    ),
                    CVProject(
                        id=row_id,
                        cv_id=cv_id,
                        position=position,
                        project_name=f"Project {position}",
                        source_project_id=row_id,
                    ),
                    Skill(skill_id=row_id, skill_name=f"Project skill {row_id}"),
                    ProjectSkill(project_id=row_id, skill_id=row_id),
                    CVSkill(
                        cv_id=cv_id,
                        skill_id=row_id,
                        category="languages",
                        position=position,
                        display_name=f"Saved skill {position}",
                    ),
                ]
            )
            for bullet_position in (2, 1):
                session.add_all(
                    [
                        CVExperienceBullet(
                            id=row_id * 10 + bullet_position,
                            cv_experience_id=row_id,
                            position=bullet_position,
                            content=f"Experience {row_id}/{bullet_position}",
                        ),
                        CVProjectBullet(
                            id=row_id * 10 + bullet_position,
                            cv_project_id=row_id,
                            position=bullet_position,
                            content=f"Project {row_id}/{bullet_position}",
                        ),
                    ]
                )
    session.flush()
    session.expunge_all()
    content = asyncio.run(load_cv_content(reader, 1))
    assert content.cv.header_snapshot == {"name": "Saved name"}
    assert [row.id for row in content.educations] == [11, 12]
    assert [item.record.id for item in content.experiences] == [11, 12]
    assert [item.record.id for item in content.projects] == [11, 12]
    for item in content.experiences:
        assert [b.content for b in item.bullets] == [
            f"Experience {item.record.id}/1",
            f"Experience {item.record.id}/2",
        ]
    for item in content.projects:
        assert [skill.skill_name for skill in item.skills] == [
            f"Project skill {item.record.id}"
        ]
        assert [b.content for b in item.bullets] == [
            f"Project {item.record.id}/1",
            f"Project {item.record.id}/2",
        ]
    assert [s.display_name for s in content.skills_by_category["languages"]] == [
        "Saved skill 1",
        "Saved skill 2",
    ]
    assert content.skills_by_category["libraries"] == ()
    assert (
        reader.scalar.await_count
        + reader.scalars.await_count
        + reader.execute.await_count
        == 8
    )


def test_empty_sections(database):
    session, reader = database
    session.add(CV(id=1, user_id=1, title="Draft", header_snapshot={}))
    session.add(CVExperience(id=1, cv_id=1, position=1))
    session.add(CVProject(id=1, cv_id=1, position=1))
    session.flush()
    content = asyncio.run(load_cv_content(reader, 1))
    assert content.educations == ()
    assert content.experiences[0].bullets == ()
    assert content.projects[0].bullets == ()
    assert content.projects[0].skills == ()
    assert all(rows == () for rows in content.skills_by_category.values())


def test_missing_cv(database):
    _, reader = database
    with pytest.raises(CVNotFoundError, match="CV 999 not found"):
        asyncio.run(load_cv_content(reader, 999))
    reader.scalars.assert_not_awaited()
