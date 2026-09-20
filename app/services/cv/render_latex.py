"""Render the resume dictionary using the MIT-licensed Jake's Resume template."""

import re
from importlib.resources import files
from typing import Any
from urllib.parse import quote, urlsplit

_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


def escape_latex(value: str) -> str:
    """Treat content as plain text, never as executable TeX."""
    return "".join(_ESCAPES.get(char, char) for char in " ".join(value.split()))


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _link(url: str, label: str) -> str:
    # Only web/email destinations; encode braces/backslashes before TeX escaping.
    try:
        scheme = urlsplit(url).scheme.lower()
    except ValueError:
        scheme = ""
    if scheme not in {"https", "http", "mailto"}:
        return escape_latex(label)
    target = quote(url, safe=":/?#[]@!$&'()*+,;=-._~%")
    return (
        r"\href{" + escape_latex(target) + r"}{\underline{" + escape_latex(label) + "}}"
    )


def _date(value: Any) -> str:
    value = _text(value)
    if not value:
        return ""
    match = re.fullmatch(r"(\d{4})(?:-(\d{2})(?:-\d{2})?)?", value)
    if not match:
        raise ValueError(f"Invalid resume date: {value!r}")
    year, month = match.groups()
    if month is None:
        return year
    if not 1 <= int(month) <= 12:
        raise ValueError(f"Invalid resume month: {value!r}")
    return f"{_MONTHS[int(month) - 1]} {year}"


def _period(row: dict[str, Any]) -> str:
    start = _date(row.get("startDate"))
    end = "Present" if row.get("is_current") is True else _date(row.get("endDate"))
    return " -- ".join(part for part in (start, end) if part)


def _command(name: str, *values: str) -> str:
    return "\\" + name + "".join("{" + escape_latex(value) + "}" for value in values)


def _bullets(row: dict[str, Any]) -> list[str]:
    bullets = [_text(item) for item in row.get("highlights", []) if _text(item)]
    if not bullets:
        return []
    return [
        r"\resumeItemListStart",
        *(_command("resumeItem", b) for b in bullets),
        r"\resumeItemListEnd",
    ]


def _header(basics: dict[str, Any]) -> list[str]:
    lines = []
    if name := _text(basics.get("name")):
        lines.append(r"\textbf{\Huge \scshape " + escape_latex(name) + "}")
    if label := _text(basics.get("label")):
        lines.append(escape_latex(label))
    contacts = []
    if phone := _text(basics.get("phone")):
        contacts.append(escape_latex(phone))
    if email := _text(basics.get("email")):
        contacts.append(_link("mailto:" + email, email))
    seen = set()
    links = [(_text(basics.get("url")), "Website")]
    links += [
        (_text(profile.get("url")), _text(profile.get("network")) or "Profile")
        for profile in basics.get("profiles", [])
        if isinstance(profile, dict)
    ]
    for url, label in links:
        if url and url not in seen:
            seen.add(url)
            label = {"github": "GitHub", "linkedin": "LinkedIn"}.get(
                label.lower(), label
            )
            contacts.append(_link(url, label))
    if contacts:
        lines.append(r"\small " + " $|$ ".join(contacts))
    if not lines:
        return []
    return [r"\begin{center}", " \\\\\n".join(lines), r"\end{center}"]


def render_latex(resume: dict[str, Any], *, show_project_skills: bool = True) -> str:
    """Return a standalone UTF-8 .tex document for pdfLaTeX.

    Does not query the database or compile a PDF. Expects to_resume_dict output;
    custom basics fields remain in the dictionary but have no automatic layout.
    The renderer uses English headings/months. Input collection order is retained.
    """
    basics = resume.get("basics", {})
    body = _header(basics)
    if summary := _text(basics.get("summary")):
        body += [r"\section{Summary}", escape_latex(summary)]
    for key, title in (
        ("education", "Education"),
        ("work", "Experience"),
        ("projects", "Projects"),
    ):
        rows = resume.get(key, [])
        if not rows:
            continue
        body += [_command("section", title), r"\resumeSubHeadingListStart"]
        for row in rows:
            if key == "education":
                degree = " in ".join(
                    _text(row.get(k))
                    for k in ("studyType", "area")
                    if _text(row.get(k))
                )
                body.append(
                    _command(
                        "resumeSubheading",
                        _text(row.get("institution")),
                        _text(row.get("location")),
                        degree,
                        _period(row),
                    )
                )
            elif key == "work":
                body.append(
                    _command(
                        "resumeSubheading",
                        _text(row.get("position")),
                        _period(row),
                        _text(row.get("name")),
                        _text(row.get("location")),
                    )
                )
                body += _bullets(row)
            else:
                heading = r"\textbf{" + escape_latex(_text(row.get("name"))) + "}"
                for field, label in (("url", "Project"), ("repositoryUrl", "Source")):
                    url = _text(row.get(field))
                    if url:
                        heading += " $|$ " + _link(url, label)
                keywords = (
                    ", ".join(
                        _text(word) for word in row.get("keywords", []) if _text(word)
                    )
                    if show_project_skills
                    else ""
                )
                command = (
                    r"\resumeProjectHeadingWithSkills"
                    if keywords
                    else r"\resumeProjectHeading"
                )
                project_heading = (
                    command + "{" + heading + "}{" + escape_latex(_period(row)) + "}"
                )
                if keywords:
                    project_heading += "{" + escape_latex(keywords) + "}"
                body.append(project_heading)
                body += _bullets(row)
        body.append(r"\resumeSubHeadingListEnd")
    skills = []
    for group in resume.get("skills", []):
        keywords = ", ".join(
            _text(word) for word in group.get("keywords", []) if _text(word)
        )
        if keywords:
            skills.append(
                r"\textbf{"
                + escape_latex(_text(group.get("name")))
                + "}: "
                + escape_latex(keywords)
            )
    if skills:
        body += [
            r"\section{Technical Skills}",
            r"\begin{itemize}[leftmargin=0.15in, label={}]",
            r"\small{\item{" + " \\\\\n".join(skills) + "}}",
            r"\end{itemize}",
        ]
    template = (
        files("app.services.cv")
        .joinpath("templates/jake.tex")
        .read_text(encoding="utf-8")
    )
    return template.replace("@@RESUME_BODY@@", "\n".join(body))
