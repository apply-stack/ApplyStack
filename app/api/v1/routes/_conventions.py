# API endpoint specifications. These modules contain documentation only.
# No handlers, decorators, dependencies, or router registrations are defined.
# The /api/v1 prefix represents the configured API version prefix.
#
# Authentication and authorization:
# All /me routes require an authenticated, active, email-verified account.
# Account identity must be resolved from the authenticated session, not a body user_id.
# Every nested resource must belong to both the authenticated user and its path parent.
# Missing and inaccessible user-owned resources return 404 to avoid existence disclosure.
# Admin routes require a separate administrative authorization policy.
# Password hashes, verification tokens, reset tokens, and internal errors are never returned.
#
# Validation and response conventions:
# List endpoints use limit=20 by default, a maximum limit of 100, and an opaque cursor.
# List responses contain items and next_cursor. Cursors are scoped to filters and sorting.
# Ordering includes a stable ID tie-breaker. Invalid filters and payloads return 422.
# Date/time values use ISO 8601; timestamps include their UTC offset.
# Career date fields use paired year/month values; unknown dates are null.
# PATCH preserves omitted fields; explicit null clears only nullable fields.
# Unknown and server-owned input fields must be rejected.
# Creates return 201 with the resource identifier; successful deletes return 204.
# Existing-resource updates return 200 unless the endpoint specifies a bodyless response.
# Uniqueness and foreign-key conflicts return 409 with a stable error code.
# Unauthenticated requests return 401; forbidden administrative access returns 403.
# Rate limits return 429. Unexpected failures return sanitized errors.
#
# Persistence boundaries:
# Multi-record writes execute in a transaction and roll back on failure.
# updated_at, created_at, matching versions, and ownership are managed by the server.
# The API does not expose direct writes to match_results, match_states, or match_runs.
# Session, token, administrative authorization, scoring, and rendering policies require
# implementation before their corresponding endpoints can be exposed.
