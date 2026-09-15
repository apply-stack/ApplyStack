# Authenticated education source records reusable across multiple CVs.
# Date ranges use start_year/start_month and end_year/end_month pairs.
# Months must be 1-12; each year/month pair is either fully present or fully null.
# The end must not precede the start; is_current=true requires an absent end date.


# GET /api/v1/me/educations
# Return paginated educations owned by the authenticated account.
# Use a deterministic date-based order with an ID tie-breaker.


# POST /api/v1/me/educations
# Create a source education with institution_name, degree, field_of_study, and optional location.
# Validate required text and date ranges. Derive user_id from authentication.
# Return 201 with the new resource. No CV is created or modified.


# GET /api/v1/me/educations/{education_id}
# Return the owned education and its complete editable source data.


# PATCH /api/v1/me/educations/{education_id}
# Update provided education fields while preserving omitted values.
# Validate the final date range after merging the patch with stored data.
# Existing CV snapshots remain unchanged.


# DELETE /api/v1/me/educations/{education_id}
# Physically delete the owned education only when foreign-key rules allow deletion.
# Return 409 when source records or saved CV references prevent deletion.
# Do not delete dependent CV snapshots or disable foreign-key constraints.
# Return 204 on success. Archival requires a separate future schema decision.
