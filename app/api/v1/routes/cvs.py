# Authenticated CV drafts, content snapshots, tailoring, and PDF output.
# Only the versioned Jake resume template is supported.
# Static routes such as /tailor must be registered before /{cv_id}.
# Selected source records and bullets must belong to the authenticated user.
# Generated text must remain grounded in supplied career facts and skills.


# GET /api/v1/me/cvs
# Return paginated CV summaries with title, target_job_id, status, and timestamps.
# Allow status and target_job_id filters; order by creation time and ID.


# POST /api/v1/me/cvs
# Create a draft from selected education, experience, project, bullet, and skill IDs.
# Validate ownership and copy selected display content in one transaction.
# Capture the current name, phone, and links in header_snapshot.
# Resolve contact_email or users.email at creation time and store the resolved value.
# Store language_code and template_version; target_job_id is optional.
# Return 201 with the draft identifier. PDF generation is a separate operation.


# POST /api/v1/me/cvs/tailor
# Accept target job_id and an optional owned source cv_id.
# Select relevant supported content and create a new editable CV draft.
# Do not overwrite the source CV or invent experience, achievements, or skills.
# Store actual selected wording and source references, not only source IDs.
# Return 201 after completion; an asynchronous job contract requires a separate design.


# GET /api/v1/me/cvs/{cv_id}
# Return saved header, selected sections, bullet wording, skill categories, and order.
# Read stored snapshots rather than reconstructing them from current source records.


# PATCH /api/v1/me/cvs/{cv_id}
# Update permitted metadata such as title; ownership and generated status are server-owned.
# Template and content changes must follow the content/render lifecycle.
# Return 409 when an incompatible generation operation is in progress.


# PUT /api/v1/me/cvs/{cv_id}/content
# Replace the full selected content in one transaction, including section ordering.
# Validate source ownership and bullet membership in the corresponding source project/experience.
# Persist CV-specific wording and copied headings, dates, and links.
# Persist cv_skills with category, positive position, and display_name.
# Prevent duplicate selections and conflicting positions.
# Do not impose a fixed minimum of three projects; selection depends on available content.
# Invalidate the previous PDF reference and return the CV to draft status.
# Do not silently reread changed profile information into existing header snapshots.
# Reject concurrent generation conflicts; rendering must not publish an outdated content version.


# POST /api/v1/me/cvs/{cv_id}/render
# Render saved CV content using its stored Jake template version.
# Escape LaTeX-special characters and disallow untrusted executable template input.
# Update generation status and store the resulting PDF outside database binary columns.
# Save pdf_storage_key only after the file has been stored successfully.
# Return 200 on completion; return 409 when the same CV is already being generated.
# On failure, record failed status without exposing renderer internals.


# GET /api/v1/me/cvs/{cv_id}/pdf
# Authorize CV ownership before returning a PDF stream or short-lived download link.
# Require a ready output corresponding to the saved content; otherwise return 409.
# Do not expose internal filesystem paths or permanent public storage credentials.


# DELETE /api/v1/me/cvs/{cv_id}
# Delete the CV and its CV-specific sections, bullets, and skill links.
# Preserve user-owned source education, experiences, projects, bullets, and master skills.
# Coordinate stored PDF cleanup with successful database deletion.
# Reject incompatible in-progress generation and return 204 after successful deletion.
