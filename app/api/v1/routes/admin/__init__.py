# Administrative API specifications.
# These endpoints are not available to ordinary users.
# Authentication alone is insufficient; explicit administrative authorization is required.
# The current account schema does not define administrative privileges.
# No administrative routes may be enabled until an authorization policy is implemented.
# Ingestion workers may call the same application services under a trusted service identity.
# Administrative writes must be auditable and must preserve database integrity constraints.
