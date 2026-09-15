# Administrative job ingestion and maintenance. Ordinary users cannot access these routes.


# POST /api/v1/admin/jobs
# Create a job with title, company, description, application URL, and source.
# Validate optional dates, work mode, employment type, and source_job_id.
# created_at records ingestion time and cannot be provided by the caller.
# Reject duplicate source/source_job_id pairs with 409; return 201 on creation.
# Do not treat pending extraction as a completed job with zero skill requirements.


# PATCH /api/v1/admin/jobs/{job_id}
# Update provided job fields or close the listing without deleting historical CVs.
# Validate the merged date range and allowed status values.
# Description changes mark skill extraction pending through the database trigger.
# Matching-relevant edits advance matching_version; clients cannot set versions directly.
# A source check may update last_seen_at without forcing unnecessary rescoring.


# PUT /api/v1/admin/jobs/{job_id}/skills
# Replace the complete requirement list atomically.
# Each entry contains an existing skill_id and an explicit boolean is_required.
# Reject duplicate skill IDs, missing boolean flags, and unknown master skills.
# An empty list means completed extraction found no requirements.
# Update changed assignments only and mark extraction completed after a successful write.
# Database triggers invalidate affected matching results; unchanged replacements remain idempotent.
