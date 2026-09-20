# Jake's Resume LaTeX export

```python
from app.services.cv import load_cv_content, to_resume_dict, render_latex

content = await load_cv_content(session, cv_id)
tex = render_latex(to_resume_dict(content))
```

`render_latex` returns a standalone UTF-8 LaTeX string. It does not compile PDFs,
write files, or update CV status. The template retains Jake's Letter/11pt layout
and macros, adds UTF-8/T1 support, and embeds the full MIT notice in every output.
Upstream: https://github.com/jakegut/resume/blob/master/resume.tex
The original license is in `app/services/cv/templates/LICENSE`.

## Seed and print

With the project's `.env` configured, from the repository root:

```sh
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed
docker compose exec -T api python -m scripts.print_cv_tex
```

If the seed is already loaded, just run the last command. It uses the latest CV;
to select a specific CV, append its ID. No database writes occur during export.

```sh
docker compose exec -T api python -m scripts.print_cv_tex 1
# Save the source to a file on the host:
docker compose exec -T api python -m scripts.print_cv_tex > resume.tex
```

Local equivalent: `.venv/bin/python -m scripts.print_cv_tex`.
Do not assume seed IDs start at 1. The seed's `--reset` option deletes existing
rows in its managed tables, not just fixtures; it is unnecessary for exporting.

## Placement and behavior

- basics: centered name/contact details, optional label and summary. Header location
  is omitted; social links use clickable network names (GitHub, LinkedIn), and
  the personal website uses Website instead of displaying the URL.
- education: institution/location, degree/area and dates.
- work: position/dates, company/location, highlights as bullets.
- projects: project name and links, dates, highlights as bullets.
- skills: category labels and comma-separated keywords.
- Dates use English month abbreviations; is_current=true renders Present.
- Missing dates remain absent; empty sections and bullet lists are omitted.
- Text is TeX-escaped. Only HTTP(S)/mailto links are clickable.
- Extra header fields without defined layout slots are not automatically printed.
- Project technologies are not inferred from the global skills list.

## Compile manually

Use pdfLaTeX in Overleaf or a TeX Live installation with the packages imported
by the template. The application Docker image does not include a TeX compiler.

```sh
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error resume.tex
```

The renderer does not truncate content or enforce a one-page limit. Inspect long
headings, links, Unicode glyphs and page breaks in the compiled output before
using it. A future server-side compiler should run with restricted filesystem
access, no network/shell execution, and time/resource limits.
