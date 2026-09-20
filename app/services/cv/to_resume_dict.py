"""Convert saved CV content to JSON Resume v1.0.0 without database access.

Schema: https://jsonresume.org/schema
The returned dict can be passed to json.dumps or an HTTP JSON response.
"""

from typing import Any

from app.models.common import MonthRangeMixin
from app.services.cv.load_cv_content import CVContent

SKILL_LABELS = {
    "languages": "Programming Languages",
    "frameworks": "Frameworks",
    "developer_tools": "Developer Tools",
    "libraries": "Libraries",
}


def _dates(record: MonthRangeMixin) -> dict[str, str | bool]:
    dates: dict[str, str | bool] = {"is_current": bool(record.is_current)}
    for key, year, month in (
        ("startDate", record.start_year, record.start_month),
        ("endDate", record.end_year, record.end_month),
    ):
        if year is None or (key == "endDate" and record.is_current):
            continue
        dates[key] = f"{year:04d}" + (f"-{month:02d}" if month is not None else "")
    return dates


def _text_fields(values: dict[str, Any]) -> dict[str, str]:
    return {
        key: value
        for key, value in values.items()
        if isinstance(value, str) and value.strip()
    }


def _without_empty(value: Any) -> Any:
    """Prune empty JSON values recursively, retaining false and zero."""
    if isinstance(value, dict):
        return {
            key: cleaned
            for key, item in value.items()
            if (cleaned := _without_empty(item)) is not None
        } or None
    if isinstance(value, list):
        return [
            cleaned for item in value if (cleaned := _without_empty(item)) is not None
        ] or None
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return value


def to_resume_dict(content: CVContent) -> dict[str, Any]:
    """Map snapshot fields to a fresh, JSON-serializable resume dictionary.

    All nonempty header fields are retained in basics alongside standard aliases.
    Missing optional fields are omitted; an empty header omits basics entirely. Collection order comes from CVContent.
    Programming languages are skills, not spoken languages. Repository URLs and
    education locations use schema-permitted extension fields. Internal IDs,
    storage keys and workflow state are not resume content.
    """
    header = _without_empty(content.header_snapshot) or {}
    basics: dict[str, Any] = dict(header)
    mapped = _text_fields(
        {
            "name": header.get("name"),
            "email": header.get("email"),
            "phone": header.get("phone"),
            "label": header.get("headline"),
            "summary": header.get("summary"),
        }
    )
    for key, value in mapped.items():
        basics.setdefault(key, value)
    location = _text_fields(
        {"city": header.get("city"), "countryCode": header.get("country_code")}
    )
    if location:
        basics.setdefault("location", location)
    links = header.get("links", {})
    if isinstance(links, dict):
        website = links.get("website")
        if isinstance(website, str) and website.strip():
            basics.setdefault("url", website)
        profiles = [
            {
                "network": {"github": "GitHub", "linkedin": "LinkedIn"}.get(
                    network, network
                ),
                "url": url,
            }
            for network, url in links.items()
            if network != "website" and isinstance(url, str) and url.strip()
        ]
        if profiles:
            basics.setdefault("profiles", profiles)

    education = [
        {
            **_text_fields(
                {
                    "institution": row.institution_name,
                    "area": row.field_of_study,
                    "studyType": row.degree,
                    "location": row.location,
                }
            ),
            **_dates(row),
        }
        for row in content.educations
    ]
    work = [
        {
            **_text_fields(
                {
                    "name": item.record.company_name,
                    "position": item.record.position_title,
                    "location": item.record.location,
                }
            ),
            **_dates(item.record),
            "highlights": [bullet.content for bullet in item.bullets],
        }
        for item in content.experiences
    ]
    projects = [
        {
            **_text_fields(
                {
                    "name": item.record.project_name,
                    "url": item.record.project_url,
                    "repositoryUrl": item.record.repository_url,
                }
            ),
            **_dates(item.record),
            "keywords": [skill.skill_name for skill in item.skills],
            "highlights": [bullet.content for bullet in item.bullets],
        }
        for item in content.projects
    ]
    return {
        **({"basics": basics} if basics else {}),
        "education": education,
        "work": work,
        "projects": projects,
        "skills": [
            {
                "name": SKILL_LABELS[category],
                "keywords": [skill.display_name for skill in rows],
            }
            for category, rows in content.skills_by_category.items()
            if rows
        ],
    }
