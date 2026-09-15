"""
Database-backed HTTP Basic authentication until session login is implemented.

Credentials must be sent over HTTPS outside localhost development. No user ID
header or query parameter can select the authenticated identity.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import func, select

from app.core.security import verify_password
from app.db.session import DbSession
from app.models.user import User, UserStatus

basic_auth = HTTPBasic()
Credentials = Annotated[HTTPBasicCredentials, Depends(basic_auth)]


async def get_current_user(credentials: Credentials, session: DbSession) -> User:
    user = await session.scalar(
        select(User).where(
            func.lower(func.btrim(User.email))
            == func.lower(func.btrim(credentials.username))
        )
    )
    # Argon2 is CPU-intensive and must not block the asynchronous event loop.
    valid = await run_in_threadpool(
        verify_password, credentials.password, user.password_hash if user else None
    )
    if not valid or user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if user.status != UserStatus.ACTIVE or user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account must be active and email verified",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
