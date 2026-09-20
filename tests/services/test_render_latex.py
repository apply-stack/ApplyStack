from copy import deepcopy

import pytest

from app.services.cv import render_latex, to_resume_dict
from tests.services.test_resume_dict import example_content


def test_render_sections_and_license():
    data = to_resume_dict(example_content())
    before = deepcopy(data)
    tex = render_latex(data)
    assert "Copyright (c) 2020 Jake Gutierrez" in tex
    assert "Permission is hereby granted" in tex
    assert r"\documentclass[letterpaper,11pt]{article}" in tex
    assert tex.count(r"\begin{document}") == 1
    assert tex.endswith("\\end{document}\n")
    assert "@@RESUME_BODY@@" not in tex
    assert (
        r"\resumeSubheading{Example University}{}{BSc in Computer Science}{Sep 2023 -- Present}"
        in tex
    )
    assert r"\resumeSubheading{Intern}{Jun 2025 -- Sep 2025}{Example Company}{}" in tex
    assert r"\resumeItem{Built an API}" in tex
    assert r"\textbf{Programming Languages}: Python" in tex
    assert "Jake Ryan" not in tex
    assert data == before


def test_empty_and_unknown_dates():
    tex = render_latex({})
    assert r"\section{Education}" not in tex
    assert r"\begin{center}" not in tex
    data = {"work": [{"name": "Company", "position": "Role", "is_current": False}]}
    tex = render_latex(data)
    assert r"\resumeSubheading{Role}{}{Company}{}" in tex
    assert "Present" not in tex
    assert "\\resumeItemListStart\n" not in tex


def test_escape_text_links_and_deduplicate():
    url = "https://example.com/a_b?q=1&x=2#part"
    data = {
        "basics": {
            "name": r"A & B 50% #1_$ {x} \input{evil}",
            "url": url,
            "profiles": [{"url": url}],
        },
        "projects": [
            {
                "name": "Demo",
                "url": "javascript:alert(1)",
                "highlights": ["İstanbul, çağrı, öğrenim"],
            }
        ],
    }
    tex = render_latex(data)
    assert r"A \& B 50\% \#1\_\$ \{x\} \textbackslash{}input\{evil\}" in tex
    assert tex.count(r"\href{https://example.com/a\_b?q=1\&x=2\#part}") == 1
    assert "javascript:" not in tex
    assert "İstanbul, çağrı, öğrenim" in tex


def test_invalid_date():
    with pytest.raises(ValueError, match="month"):
        render_latex({"education": [{"startDate": "2025-13"}]})


def test_project_skills_toggle_and_order():
    resume = {
        "projects": [
            {
                "name": "Example",
                "keywords": ["C#", "FastAPI"],
                "highlights": ["Built an API"],
            }
        ]
    }
    before = deepcopy(resume)
    shown = render_latex(resume)
    hidden = render_latex(resume, show_project_skills=False)
    assert r"{C\#, FastAPI}" in shown
    assert (
        shown.index(r"\textbf{Example}")
        < shown.index(r"{C\#, FastAPI}")
        < shown.index(r"\resumeItem{Built an API}")
    )
    assert "FastAPI" not in hidden
    assert r"\resumeItem{Built an API}" in hidden
    assert resume == before
    assert r"\textit{}" not in render_latex({"projects": [{"name": "Empty"}]})


@pytest.mark.parametrize(
    "project_url, repository_url",
    [
        (None, None),
        ("https://example.com", None),
        (None, "https://github.com/example/repo"),
        ("https://example.com", "https://github.com/example/repo"),
        ("https://example.com", "https://example.com"),
    ],
)
def test_project_links_are_independent(project_url, repository_url):
    original = example_content()
    original.projects[0].record.project_url = project_url
    original.projects[0].record.repository_url = repository_url
    tex = render_latex(to_resume_dict(original))
    assert (r"\underline{Project}" in tex) == bool(project_url)
    assert (r"\underline{Source}" in tex) == bool(repository_url)
