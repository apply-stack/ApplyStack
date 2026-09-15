# Authenticated personal profile management.


# GET /api/v1/me/profile
# Return the profile or 404 if profile completion has not occurred.
# Return contact_email as stored and expose resolved CV email as a derived field.
# The derived email uses contact_email when present, otherwise the current account email.


# PUT /api/v1/me/profile
# Create or replace the complete profile for the authenticated account.
# Require nonblank name and surname; normalize empty optional text to null.
# Validate email, phone, country code, and supported URL formats at the API boundary.
# Return 201 for creation and 200 for replacement; omitted optional fields are cleared.
# Profile changes do not rewrite stored CV snapshots.


# PATCH /api/v1/me/profile
# Update only provided profile fields; return 404 when the profile does not exist.
# Reject null or blank values for mandatory fields.
# An explicit null contact_email restores the account-email fallback for future CVs.
# Name and contact changes do not invalidate the skill-only matching cache.
