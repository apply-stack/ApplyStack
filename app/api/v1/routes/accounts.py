# Authenticated account access and lifecycle operations.

from fastapi import APIRouter, Response

from app.api.dependencies.auth import CurrentUser
from app.schemas.account import AccountResponse

router = APIRouter(prefix="/me", tags=["accounts"])


# GET /api/v1/me
# Return the authenticated account ID, email, status, and permitted account timestamps.
# Exclude password_hash and authentication secrets from the response schema.
@router.get(
    "",
    responses={
        401: {"description": "Missing or invalid credentials"},
        403: {"description": "Account is not active and verified"},
    },
)
async def read_me(user: CurrentUser, response: Response) -> AccountResponse:
    response.headers["Cache-Control"] = "no-store"
    return AccountResponse.model_validate(user)


# PATCH /api/v1/me/password
# Require the current password and a valid replacement password.
# Verify the current password and store the replacement as an Argon2id hash.
# Revoke other sessions according to policy; account and profile records remain intact.


# POST /api/v1/me/deactivate
# Set account status to deactivated and revoke active sessions.
# Preserve profiles, skills, career records, CVs, and matching data.
# This operation performs no physical user deletion. Return 204 on success.
