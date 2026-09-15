# Read-only skill catalog access and authenticated user skill assignments.


# GET /api/v1/skills
# Search the master catalog with q and return paginated skill_id/skill_name pairs.
# Support case-insensitive search while preserving meaningful punctuation in C++, C#, and C.
# Use skill_name then skill_id for deterministic ordering.
# Search and user assignments never create master skill records.


# GET /api/v1/me/skills
# Return the authenticated user's skill assignments with their catalog names.
# Use pagination and deterministic ordering.


# PUT /api/v1/me/skills/{skill_id}
# Assign an existing catalog skill to the authenticated user.
# Return 404 for an unknown skill; repeated assignment is idempotent.
# Return 201 for a new assignment and 200 for an existing assignment.
# An actual insert advances the user matching version through the database trigger.


# DELETE /api/v1/me/skills/{skill_id}
# Remove only the user-to-skill assignment; preserve the master skill record.
# Return 204, including when the assignment is already absent.
# An actual deletion invalidates cached matches through the user version trigger.
# Previously generated CV skill snapshots are retained.
