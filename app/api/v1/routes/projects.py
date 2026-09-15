# Authenticated project source records reusable across multiple CVs.
# Date ranges use start_year/start_month and end_year/end_month pairs.
# Months must be 1-12; each year/month pair is either fully present or fully null.
# The end must not precede the start; is_current=true requires an absent end date.


# GET /api/v1/me/projects
# Return paginated projects owned by the authenticated account.
# Use a deterministic date-based order with an ID tie-breaker.


# POST /api/v1/me/projects
# Create a source project with project_name and optional project_url and repository_url.
# Validate required text and date ranges. Derive user_id from authentication.
# Return 201 with the new resource. No CV is created or modified.


# GET /api/v1/me/projects/{project_id}
# Return the owned project and its complete editable source data.
# Include ordered description bullets and associated skill names.


# PATCH /api/v1/me/projects/{project_id}
# Update provided project fields while preserving omitted values.
# Validate the final date range after merging the patch with stored data.
# Existing CV snapshots remain unchanged.


# DELETE /api/v1/me/projects/{project_id}
# Physically delete the owned project only when foreign-key rules allow deletion.
# Return 409 when source records or saved CV references prevent deletion.
# Do not delete dependent CV snapshots or disable foreign-key constraints.
# Return 204 on success. Archival requires a separate future schema decision.


# POST /api/v1/me/projects/{project_id}/bullets
# Create a nonblank explanation bullet under the owned parent.
# Accept a positive position or append using a transaction-safe allocation.
# Each bullet represents a semantic item, not a physical PDF line.
# Return 201; duplicate positions are rejected with 409.


# PATCH /api/v1/me/projects/{project_id}/bullets/{bullet_id}
# Validate both parent ownership and the bullet-to-parent relationship.
# Update the source content; saved CV wording remains unchanged.
# Use the ordering endpoint for multi-bullet reorder operations.


# DELETE /api/v1/me/projects/{project_id}/bullets/{bullet_id}
# Delete the owned source bullet when no saved CV references prevent deletion.
# Return 409 if referenced by a CV; retain all saved CV content.


# PUT /api/v1/me/projects/{project_id}/bullets/order
# Accept the complete ordered list of current bullet IDs without duplicates.
# Require every ID to belong to the specified parent and reject missing/extra IDs.
# Assign positive positions atomically without transient uniqueness violations.


# PUT /api/v1/me/projects/{project_id}/skills/{skill_id}
# Assign an existing catalog skill to the owned project.
# Return 201 for creation and 200 if already assigned; unknown skills return 404.
# This operation does not add a user skill or rewrite saved CV skills.


# DELETE /api/v1/me/projects/{project_id}/skills/{skill_id}
# Remove only the project-to-skill assignment; return 204 if already absent.
# Keep the master skill, user skill assignments, and saved CV skill snapshots.
