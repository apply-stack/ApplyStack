from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import SettingsDep

router = APIRouter(tags=["meta"])


class MetaResponse(BaseModel):
    name: str
    version: str
    environment: str


@router.get("/")
async def read_meta(settings: SettingsDep) -> MetaResponse:
    return MetaResponse(
        name=settings.project_name,
        version=settings.version,
        environment=settings.environment,
    )