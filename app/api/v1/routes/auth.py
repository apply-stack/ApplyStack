# Authentication, email verification, and password recovery.
# Public authentication routes are rate-limited. Token values must not be logged.
# Session transport, expiration, revocation, and CSRF protections must be defined
# before implementation. Verification and reset flows require token persistence.


# POST /api/v1/auth/register
# Create an account from email and a plaintext password transmitted over HTTPS.
# Validate and normalize email consistently with database uniqueness rules.
# Hash the password with Argon2id on the server; never accept password_hash input.
# Set status to pending_verification and issue a single-use verification token.
# Persist account creation before dispatching the verification message.
# Use an account-enumeration-resistant response policy for existing email addresses.
# Profile creation is separate unless mandatory name and surname are supplied by a defined flow.


# POST /api/v1/auth/verify-email
# Validate a purpose-bound, unexpired, single-use verification token.
# Set email_verified_at and activate only an account awaiting verification.
# Do not reactivate suspended or deactivated accounts through this operation.
# Consume the token and update the account atomically.


# POST /api/v1/auth/resend-verification
# Accept an email address and request a new verification message when eligible.
# Return a generic acknowledgement whether or not the account exists.
# Apply resend cooldowns and define replacement-token invalidation behavior.


# POST /api/v1/auth/login
# Verify email and password and require an active, verified account.
# Return or establish a session according to the selected authentication transport.
# Use generic invalid-credential responses and rate-limit repeated failures.


# POST /api/v1/auth/logout
# Invalidate the current session and clear authentication cookies when applicable.
# Return 204. Repeated logout must not create an error or a new session.
# Token-based implementations must define server-side revocation semantics.


# POST /api/v1/auth/forgot-password
# Accept an email address and initiate a single-use password reset when eligible.
# Return the same acknowledgement for known and unknown email addresses.
# Apply rate limits and store only a secure representation of the reset token.


# POST /api/v1/auth/reset-password
# Validate the reset token and password policy, then store a fresh Argon2id hash.
# Consume the token atomically and revoke existing sessions under the session policy.
# Password reset does not verify email or reactivate a disabled account.
