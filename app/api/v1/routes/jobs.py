# Read-only job browsing. Job ingestion and edits belong to administrative services.


# GET /api/v1/jobs
# Return a paginated list of job summaries.
# Filters: q, company, location, work_mode, employment_type, repeated skill_id,
# skill_match=all|any, created_after, and open_only.
# q searches title and description; created_after refers to database ingestion time.
# open_only requires open status and a currently valid known application date range.
# Unknown date bounds do not independently exclude a job.
# Sort options: newest and deadline; include job_id as a deterministic tie-breaker.
# Place unknown deadlines last. Apply limit and cursor after all filters.
# Use EXISTS or equivalent filtering so skill joins do not duplicate jobs.


# GET /api/v1/jobs/{job_id}
# Return the full description, company, dates, application URL, and source information.
# Include job skills with skill_id, skill_name, and is_required.
# Distinguish pending extraction from a completed extraction with no requirements.
# Return 404 when the job does not exist.
