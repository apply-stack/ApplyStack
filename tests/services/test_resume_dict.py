import json
from copy import deepcopy

from app.models.cv import (
    CV,
    CVEducation,
    CVExperience,
    CVExperienceBullet,
    CVProject,
    CVSkill,
)
from app.services.cv import CVContent, to_resume_dict
from app.services.cv.load_cv_content import ExperienceContent, ProjectContent


def example_content():
    return CVContent(
        cv=CV(
            header_snapshot={
                "name": "Deniz Yilmaz",
                "email": "deniz@example.com",
                "city": "Istanbul",
                "country_code": "TR",
                "links": {
                    "github": "https://github.com/example",
                    "website": "https://example.com",
                },
            }
        ),
        educations=(
            CVEducation(
                institution_name="Example University",
                degree="BSc",
                field_of_study="Computer Science",
                start_year=2023,
                start_month=9,
                is_current=True,
            ),
        ),
        experiences=(
            ExperienceContent(
                CVExperience(
                    company_name="Example Company",
                    position_title="Intern",
                    start_year=2025,
                    start_month=6,
                    end_year=2025,
                    end_month=9,
                    is_current=False,
                ),
                (CVExperienceBullet(content="Built an API"),),
            ),
        ),
        projects=(
            ProjectContent(
                CVProject(
                    project_name="Example project",
                    repository_url="https://github.com/example/project",
                ),
                (),
            ),
        ),
        skills_by_category={
            "languages": (CVSkill(display_name="Python"),),
            "libraries": (),
        },
    )


def test_resume_mapping_and_json_serialization():
    content = example_content()
    before = deepcopy(content.cv.header_snapshot)
    resume = to_resume_dict(content)
    assert json.loads(json.dumps(resume)) == resume
    assert resume["basics"]["location"] == {"city": "Istanbul", "countryCode": "TR"}
    assert resume["basics"]["profiles"] == [
        {"network": "GitHub", "url": "https://github.com/example"}
    ]
    assert resume["basics"]["url"] == "https://example.com"
    assert resume["education"] == [
        {
            "institution": "Example University",
            "area": "Computer Science",
            "studyType": "BSc",
            "startDate": "2023-09",
            "is_current": True,
        }
    ]
    assert resume["work"][0]["endDate"] == "2025-09"
    assert resume["work"][0]["highlights"] == ["Built an API"]
    assert "url" not in resume["projects"][0]
    assert (
        resume["projects"][0]["repositoryUrl"] == "https://github.com/example/project"
    )
    assert resume["skills"] == [
        {"name": "Programming Languages", "keywords": ["Python"]}
    ]
    assert "languages" not in resume
    resume["basics"]["profiles"][0]["url"] = "changed"
    assert content.cv.header_snapshot == before


def test_optional_fields_and_current_dates():
    content = example_content()
    content.cv.header_snapshot = {"name": "", "email": None, "links": None}
    content.experiences[0].record.is_current = True
    content.projects[0].record.project_url = "https://example.com/project"
    resume = to_resume_dict(content)
    assert "basics" not in resume
    assert "endDate" not in resume["work"][0]
    assert "startDate" not in resume["projects"][0]
    assert resume["projects"][0]["url"] == "https://example.com/project"
    assert (
        resume["projects"][0]["repositoryUrl"] == "https://github.com/example/project"
    )


def test_empty_resume():
    resume = to_resume_dict(CVContent(CV(header_snapshot={}), (), (), (), {}))
    assert "basics" not in resume
    assert all(resume[key] == [] for key in ("education", "work", "projects", "skills"))


def test_complete_header_and_empty_values():
    content = example_content()
    content.cv.header_snapshot = {
        "name": "Deniz",
        "custom": {"text": "Keep", "empty": "  "},
        "items": [None, "", {"empty": []}, "Keep"],
        "zero": 0,
        "flag": False,
        "empty": {},
        "profiles": [{"network": "Custom", "url": "https://example.com"}],
    }
    before = deepcopy(content.cv.header_snapshot)
    resume = to_resume_dict(content)
    assert resume["basics"] == {
        "name": "Deniz",
        "custom": {"text": "Keep"},
        "items": ["Keep"],
        "zero": 0,
        "flag": False,
        "profiles": [{"network": "Custom", "url": "https://example.com"}],
    }
    resume["basics"]["custom"]["text"] = "Changed"
    assert content.cv.header_snapshot == before
    assert content.header_snapshot == before
    assert resume["education"][0]["is_current"] is True
    assert resume["work"][0]["is_current"] is False
    assert resume["projects"][0]["is_current"] is False


def test_unknown_end_date_is_distinct_from_current():
    content = example_content()
    record = content.experiences[0].record
    record.end_year = record.end_month = None
    resume = to_resume_dict(content)
    assert resume["work"][0]["is_current"] is False
    assert "endDate" not in resume["work"][0]
    record.is_current = True
    resume = to_resume_dict(content)
    assert resume["work"][0]["is_current"] is True
    assert "endDate" not in resume["work"][0]


def test_project_skills_use_catalog_names():
    from app.models.skill import Skill

    original = example_content()
    project = original.projects[0]
    content = CVContent(
        original.cv,
        original.educations,
        original.experiences,
        (
            ProjectContent(
                project.record,
                project.bullets,
                (
                    Skill(skill_name="Python"),
                    Skill(skill_name="FastAPI"),
                ),
            ),
        ),
        original.skills_by_category,
    )
    assert to_resume_dict(content)["projects"][0]["keywords"] == [
        "Python",
        "FastAPI",
    ]
