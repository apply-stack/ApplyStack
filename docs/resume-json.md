# CV → JSON Resume

The converter targets JSON Resume v1.0.0:
- Format and full example: https://jsonresume.org/schema
- Versioned schema: https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json
- Local output example: [resume.example.json](../fixtures/resume.example.json)

```python
from app.services.cv import load_cv_content, to_resume_dict

content = await load_cv_content(session, cv_id)
resume = to_resume_dict(content)
# Optional text serialization:
# json.dumps(resume, ensure_ascii=False)
```

`to_resume_dict` returns a fresh dictionary and performs no database queries.
Authorize access before loading a user's CV. It uses only saved snapshots.

| Saved content | JSON Resume |
| --- | --- |
| Header name/email/phone/headline/summary | basics.name/email/phone/label/summary |
| Header city/country_code | basics.location.city/countryCode |
| Header links.website | basics.url |
| Other header links | basics.profiles |
| Education institution/field/degree | education institution/area/studyType |
| Experiences and bullets | work and highlights |
| Projects and bullets | projects and highlights |
| Categorized skill display names | skills name/keywords |

All nonempty header_snapshot fields are retained in basics, including custom fields,
alongside standard aliases. Existing keys take precedence over aliases.
Nulls, whitespace-only strings, and empty objects/arrays are removed recursively;
false and zero are preserved. An empty header omits basics.
Education, work, and projects include an explicit is_current boolean extension.

Dates retain year/month precision. Missing values are omitted, and current
entries omit endDate. Empty sections are arrays. Programming languages belong
in skills, not the spoken-languages section. CV language_code does not imply
that the person speaks that language.

Project url uses only project_url; repositoryUrl uses only repository_url.
Missing links are omitted independently. repositoryUrl and
education location are extension fields permitted by the schema, though themes
may ignore them. Internal IDs, PDF keys and workflow metadata are excluded.

This is a data format; a visual PDF/HTML theme is a separate rendering step.


## Seed and print

From the repository root, with `.env` configured:

```sh
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed
docker compose exec -T api python -m scripts.print_cv_json
```

Omitting the ID selects the latest CV. To select one explicitly:

```sh
docker compose exec -T api python -m scripts.print_cv_json 1
```

Seed IDs are not necessarily 1; reset does not reset sequences.
If records exist, seeding refuses to overwrite them. For a disposable development
database, run `docker compose exec api python -m scripts.seed --reset`.
This deletes existing rows (not only fixtures) in the seed-managed tables,
including users, jobs, CVs and matching data. The skills catalog is retained.

To save JSON locally:

```sh
docker compose exec -T api python -m scripts.print_cv_json > /tmp/resume.json
```

For a local API environment with DATABASE_URL pointing to the running database:

```sh
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed
.venv/bin/python -m scripts.print_cv_json
```
