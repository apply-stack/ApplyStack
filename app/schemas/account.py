"""Public account response. Authentication secrets are deliberately excluded."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserStatus


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    status: UserStatus
    email_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
