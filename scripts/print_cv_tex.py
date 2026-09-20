"""Print a stored CV as LaTeX: python -m scripts.print_cv_tex 1.

Omit the ID to print the most recently created CV (useful after seeding).
"""

import argparse
import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal, engine
from app.models import CV
from app.services.cv import (
    CVNotFoundError,
    load_cv_content,
    render_latex,
    to_resume_dict,
)


async def run(cv_id: int | None, *, show_project_skills: bool = True) -> None:
    # Keep stdout valid LaTeX even when SQL_ECHO is enabled in local settings.
    engine.echo = False
    try:
        async with AsyncSessionLocal() as session:
            if cv_id is None:
                cv_id = await session.scalar(
                    select(CV.id).order_by(CV.created_at.desc(), CV.id.desc()).limit(1)
                )
            if cv_id is None:
                raise CVNotFoundError("No CV found. Run python -m scripts.seed first.")
            content = await load_cv_content(session, cv_id)
            print(
                render_latex(
                    to_resume_dict(content), show_project_skills=show_project_skills
                ),
                end="",
            )
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cv_id", nargs="?", type=int, help="Defaults to the latest CV")
    parser.add_argument(
        "--show-project-skills",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show project skill names below project headings (default: enabled)",
    )
    args = parser.parse_args()
    try:
        asyncio.run(run(args.cv_id, show_project_skills=args.show_project_skills))
    except CVNotFoundError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
