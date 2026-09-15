# Administrative master skill catalog maintenance. Ordinary users cannot access these routes.


# POST /api/v1/admin/skills
# Create a nonblank canonical skill name with a server-generated sequential ID.
# Enforce case-insensitive, trimmed uniqueness and preserve meaningful punctuation.
# Return 201, or 409 when the normalized name already exists.
# Do not implicitly create aliases or import an external catalog.


# PATCH /api/v1/admin/skills/{skill_id}
# Rename a catalog skill after validating normalized uniqueness.
# Preserve its ID and existing user/job/project/CV associations.
# Stored CV display names remain unchanged.
# Skill deletion is not exposed because existing foreign-key references must be preserved.
