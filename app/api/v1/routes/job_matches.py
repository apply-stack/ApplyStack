# Authenticated on-demand job matching.
# No scheduler or next_run_at field is used. Results are refreshed during the request.
# The scoring policy must be versioned and supplied by the matching service.
# A percentage represents algorithmic compatibility, not hiring probability.


# GET /api/v1/me/job-matches
# Return matching jobs ordered by percentage descending and job_id as a tie-breaker.
# Accept min_percentage from 0 through 100, limit, cursor, company, work_mode,
# and employment_type. limit is the requested top-k result count.
# Check user, job, and scoring versions before serving cached results.
# Compute only missing or stale eligible pairs; user-skill or algorithm changes
# invalidate all affected open jobs. Updated old jobs must also be reconsidered.
# Eligible jobs are open, within known application date bounds, and have completed extraction.
# Persist low scores as well as high scores; threshold and filter changes do not rescore jobs.
# Apply response filters and pagination to valid results, not to an incomplete scoring batch.
# Serialize concurrent requests per user so they do not duplicate computation.
# Wait for required computation before returning; never label stale results as current.
# Return job summaries, percentage, computed_at, and next_cursor.
# Bind pagination cursors to the result generation; reject obsolete cursors with 409.
# Refresh failures return a sanitized error and do not advance successful matching state.


# GET /api/v1/me/job-matches/{job_id}
# Return the authenticated user's current compatibility score for one eligible job.
# Reuse a valid result or compute the missing/stale pair through the matching service.
# A single-job refresh must not mark the entire user catalog as fully refreshed.
# Return 404 for a missing job and 409 when scoring is unavailable because the job
# is closed, outside the application window, or awaiting skill extraction.
